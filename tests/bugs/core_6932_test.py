#coding:utf-8

"""
ID:          issue-6932
ISSUE:       6932
TITLE:       GTT's pages are not released while dropping it
DESCRIPTION:
    We extract value of config parameter 'TempTableDirectory' in order to get directory where GTT data are stored.
    If this parameter is undefined then we query environment variables: FIREBIRD_TMP; TEMP and TMP - and stop after
    finding first non-empty value in this list. Name of this folder is stored in GTT_DIR variable.

    Then we create GTT and add some data in it; file 'fb_table_*' will appear in <GTT_DIR> after this.
    We have to obtain size of this file and invoke os.path.getsize(). Result will be NON-zero, despite that Windows
    'dir' command shows that this file has size 0. We initialize list 'gtt_size_list' and save this size in it as
    'initial' element (with index 0).

    After this, we make loop for <ITER_COUNT> iterations and do on each of them:
      * drop GTT;
      * create GTT (with new name);
      * add some data into just created GTT
      * get GTT file size and add it to the list for further analysis (see 'gtt_size_list.append(...)')

    Finally, we scan list 'gtt_size_list' (starting from 2nd element) and evaluate DIFFERENCE between size of GTT file
    that was obtained on Nth and (N-1)th iterations. MEDIAN value of this difference must be ZERO.

    NB-1.
    BEFORE this ticket was fixed, size of GTT grew noticeably only for the first ~10 iterations.
    This is example how size was changed (in percents):
      26.88
      34.92
      12.69
      19.84
      11.91
      10.64
      14.43
       8.40
       7.75
    For big numbers of ITER_COUNT values quickly tend to zero.
    AFTER this fix size is changed only for 2nd iteration (and not in every measure), for ~6%.
    All rest changes (startingfrom 3rd measure) must be zero.

    NB-2. Test implemented for Windows only: there is no ability to get name of GTT file on Linux
    because all such files marked as deleted immediately after creation.

FBTEST:      bugs.core_6932
NOTES:
    [20.06.2022] pzotov
    Confirmed bug on 3.0.6.33301; 5.0.0.169.
    Checked on WINDOWS builds: 3.0.8.33535, 4.0.1.2692, T5.0.0.509
"""

import os
import sys
import glob
import pytest
from firebird.qa import *
from firebird.driver import TPB, Isolation

#--------------------------------------------------------------------
def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None
#--------------------------------------------------------------------


db = db_factory()

act = python_act('db')

#custom_tpb = TPB(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0, auto_commit = True)
custom_tpb = TPB(lock_timeout=0) #, auto_commit = True)

ITER_COUNT = 30
FB_GTT_PATTERN = 'fb_table_*'

expected_stdout_gtt_size_median = """
    GTT file size remains the same.
"""

@pytest.mark.version('>=3.0.9')
@pytest.mark.platform('Windows')
def test_1(act: Action, capsys):
    
    GTT_DIR = ''
    GTT_CREATE_TABLE = "recreate global temporary table gtt_%(gtt_name_idx)s(s varchar(1000) unique) on commit preserve rows"
    GTT_ADD_RECORDS = "insert into gtt_%(gtt_name_idx)s select lpad('', 1000, uuid_to_char(gen_uuid())) from rdb$types,rdb$types rows 1000"
    GTT_DROP_TABLE = "drop table gtt_%(gtt_prev_idx)s"
    with act.db.connect() as con:
        tx1 = con.transaction_manager(default_tpb=custom_tpb.get_buffer())
        tx1.begin()
        cur = tx1.cursor()

        #cur.execute("select coalesce(rdb$config_value,'') from rdb$config where rdb$config_name = 'TempTableDirectory'")
        #for r in cur:
        #    GTT_DIR = r[0]

        if not GTT_DIR:
            for p in ('FIREBIRD_TMP', 'TEMP', 'TMP'):
                GTT_DIR = os.environ.get(p, '')
                if GTT_DIR:
                    break

        if not GTT_DIR:
            print('### ABEND ### Could not get directory where GTT data are stored.')

        assert GTT_DIR
        act.reset()

        gtt_dir_init = glob.glob( os.path.join(GTT_DIR, FB_GTT_PATTERN) )
        gtt_name_idx = 0

        cur.execute(GTT_CREATE_TABLE % locals())
        tx1.commit()

        cur.execute(GTT_ADD_RECORDS % locals())
        tx1.commit()

        gtt_dir_curr = glob.glob( os.path.join(GTT_DIR, FB_GTT_PATTERN) )
        gtt_new_file = list(set(gtt_dir_curr) - set(gtt_dir_init))[0]
        gtt_size_list = [ (0,os.path.getsize(gtt_new_file)) ]

        for gtt_name_idx in range(1,ITER_COUNT):
            # print('Iter No %d' % gtt_name_idx)
            gtt_prev_idx = gtt_name_idx-1
            cur.execute(GTT_DROP_TABLE % locals())
            tx1.commit()
            cur.execute(GTT_CREATE_TABLE % locals())
            tx1.commit()
            cur.execute(GTT_ADD_RECORDS % locals())
            tx1.commit()
            gtt_size_list.append( (gtt_name_idx,os.path.getsize(gtt_new_file)) )

        size_changes_percent_list = []
        for k in range(1,len(gtt_size_list)):
            size_changes_percent_list.append( 100.00 * gtt_size_list[k][1] / gtt_size_list[k-1][1] - 100 )

        median_size_change_percent = median(size_changes_percent_list)

        if median_size_change_percent == 0:
            print( 'GTT file size remains the same.' )
        else:
            print('GTT file size UNEXPECTEDLY INCREASED. Check percentage:')
            for p in size_changes_percent_list:
                print( '{:.2f}'.format(p) )

        act.stdout = capsys.readouterr().out
        act.expected_stdout = expected_stdout_gtt_size_median
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
 
