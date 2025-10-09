#coding:utf-8

"""
ID:          issue-5878
ISSUE:       5878
TITLE:       Gradual slowdown compilation (create, recreate or drop) of views
DESCRIPTION:
    Problem was fixed 26-oct-2018 in:
        https://github.com/FirebirdSQL/firebird/commit/2cb9e648315b9f1ec925e48618b0678a1b9959fe
    Test measures difference between cpu.user_time values for two DDL sets:
        1) creation of simplest ("dummy") view like 'select 1 x from rdb$database',
           which is repeated for <DUMMY_VIEW_LOOP_CNT> times in order to accumulate
           some total that for sure will be non-zero;
        2) creation of <VIEWS_COUNT> complex ("real") views with DDL from ticket, i.e.:
              create or alter view v_test_n (f_0, f_1, ..., f_<FIELDS_COUNT>) as
              select
                 (select ... from rdb$database where rdb$relation_id = d.rdb$relation_id), -- field 0
                 (select ... from rdb$database where rdb$relation_id = d.rdb$relation_id), -- field 1
                 ...
                 (select ... from rdb$database where rdb$relation_id = d.rdb$relation_id), -- field <FIELDS_COUNT-1>
              from rdb$database as d;
           (it is crusial for this test to set <FIELDS_COUNT> to max possible value, currently this is 255).
    Actions in "1" and "2" are repeated for <N_MEASURES> times and for each iteration we add total CPU_diff time to appropriate list.
    When all <N_MEASURES> iterations pass, we evaluate median values for each list ('dummy_view_median' and 'real_view_median').
    Finally, we compare ratio real_view_median / dummy_view_median with threshold <MAX_RATIO> that was found during lot of runs
    during test implemenation.
JIRA:        CORE-5612
FBTEST:      bugs.core_5612
NOTES:
    [09.10.2025] pzotov
    1. Previous version could not verify anithing: it just checked presense of some indices in the RDB table(s).
       Actual problem (slowdown of time that needed for creation complex view) did not checked at all.
       One need to AVOID check presense of any RDB indices for tests related to performance because they may be changed/disappeared
       in the future! Letter from dimitr 08-oct-2025 08:50 ("3e3b75: Re-add indexes for object name without schema name..."):
       "... the newly added system indices are a temporary solution and may disappear in future versions...
        Maybe some of the failing tests should be re-implemented to be based on user tables instead of the system ones."
    2. During re-implementing it was found that:
       * BEFORE fix ratio between medians was in scope 16.5 ... 18.5 (4.0.0.1227, 29-sep-2018) 
       * AFTER fix ratio mostly belongs to scopes:
         ** 4.0.0.1346 (17-dec-2018): 12.7 ... 14.2 (max detected: 15.6)
         ** 4.0.7.3236: 13.4 ... 13.8 (max detected: 15.9)
         ** 5.0.4.1711: 13.2 ... 13.7 (max detected: 15.6)
         ** 6.0.0.1299: 12.3 ... 12.7 (max detected: 14.3)
       (checked on Windows, ServerMode = Super)
    3. Probably, values of <MAX_RATIO> should be adjusted for different OS /  ServerMode.
    4. Comparison of view creation time with duration of loop that invokes scalar func without affecting on I/O (e.g. gen_uuid() etc)
       can not be used in this test: differences in medians ratio between snapshots before and after fix will be very low.

    Test duration time: ~25s.
    Checked on 6.0.0.1299; 5.0.4.1711; 4.0.7.3236.
"""
import os
import psutil
from pathlib import Path
import time
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

###########################
###   S E T T I N G S   ###
###########################

# How many times we do measure:
N_MEASURES = 11

# How many times we must recreate dummy view ('select 1 x from ...') on each measure.
# Total CPU time of all creations of this view will be added to the list for further
# evaluation of MEDIAN for these values. It will serve as denominator at final step:
#
DUMMY_VIEW_LOOP_CNT = 50

# How many "real" views (with DDL from the ticket) must be created on each measure.
# Total CPU time of all creations of this view will be added to the list for further
# evaluation of MEDIAN for these values. It will serve as nominator at final step:
#
VIEWS_COUNT = 5

# How many fields per "real" view
# NB: to reproduce problem, this values must be as large as possible!
FIELDS_COUNT = 250

# Max allowed ratio between median values of CPU time measured for creation of
# <VIEWS_COUNT> "real" views vs <DUMMY_VIEW_LOOP_CNT> "dummy" views.
# NB: this value probably needs to be adjusted for different OS / ServerMode.
#
MAX_RATIO = 16.0 if os.name == 'nt' else 16.0
#MAX_RATIO = 0.

db = db_factory()
act = python_act('db')
tmp_sql = temp_file('tmp_core_5612.sql')

#--------------------------------------------------------------------
def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None
#--------------------------------------------------------------------

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_sql: Path, capsys):

    # create or alter view v_test_n (f_0, f_1, ..., f_249) as
    # select 
    #    (select rdb$description from rdb$database where rdb$relation_id = d.rdb$relation_id),
    #    (select rdb$relation_id from rdb$database where rdb$relation_id = d.rdb$relation_id),
    #    ...
    #    (select rdb$relation_id from rdb$database where rdb$relation_id = d.rdb$relation_id),
    # from rdb$database as d;

    v_fields_in_hdr = ','.join( [ f'f_{i}' for i in range(FIELDS_COUNT) ] )
    v_fields_in_sql = '\n,'.join( [f'(select rdb$description from rdb$database where rdb$relation_id = d.rdb$relation_id)' for i in range(FIELDS_COUNT)] )
    v_ddl_lst = [ f'\ncreate or alter view v_test_{i}({v_fields_in_hdr}) as\nselect\n' + v_fields_in_sql + '\nfrom rdb$database as d;' for i in range(VIEWS_COUNT)]

    # 4debug, remove after:
    #with open(r'c:\temp\tmp_5612.sql', 'w') as f:
    #   f.write( '\n'.join(v_ddl_lst) )
    #assert 1 == 0

    times_map = {}
    with act.db.connect() as con:
        cur=con.cursor()
        cur.execute('select mon$server_pid as p from mon$attachments where mon$attachment_id = current_connection')
        fb_pid = int(cur.fetchone()[0])

        for i in range(0, N_MEASURES):
            try:

                fb_info_init = psutil.Process(fb_pid).cpu_times()
                for k in range(DUMMY_VIEW_LOOP_CNT):
                    con.execute_immediate('create or alter view v_dummy as select 1 x from rdb$database')
                    #con.execute_immediate('recreate sequence g')
                    con.commit()
                fb_info_curr = psutil.Process(fb_pid).cpu_times()
                times_map[ 'dummy_view', i ]  = max(fb_info_curr.user - fb_info_init.user, 0.000001)

                fb_info_init = psutil.Process(fb_pid).cpu_times()
                for v in v_ddl_lst:
                    con.execute_immediate(v)
                    con.commit()
                fb_info_curr = psutil.Process(fb_pid).cpu_times()
                times_map[ 'real_view', i ]  = max(fb_info_curr.user - fb_info_init.user, 0.000001)

            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)

    dummy_view_median = median([v for k,v in times_map.items() if k[0] == 'dummy_view'])
    real_view_median = median([v for k,v in times_map.items() if k[0] == 'real_view'])
    median_ratio = real_view_median / dummy_view_median

    EXPECTED_MSG = f'acceptable, median_ratio less than {MAX_RATIO=}'
    print( 'Medians ratio: ' + (EXPECTED_MSG if median_ratio <= MAX_RATIO else '/* perf_issue_tag */ POOR: %s, more than threshold: %s' % ( '{:9g}'.format(median_ratio), '{:9g}'.format(MAX_RATIO) ) ) )

    if median_ratio > MAX_RATIO:
        print(f'CPU times for each of {N_MEASURES} measures:')
        for what_measured in ('dummy_view', 'real_view', ):
            print(f'{what_measured=}:')
            for p in [v for k,v in times_map.items() if k[0] == what_measured]:
                print(p)

    act.expected_stdout = f"""
        Medians ratio: {EXPECTED_MSG}
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
