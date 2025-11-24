#coding:utf-8

"""
ID:          issue-8799
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8799
TITLE:       BUGCHECK "decompression overran buffer (179)" when WITH LOCK clause is used
DESCRIPTION:
NOTES:
    [25.11.2024] pzotov
    Confirmed bug on 6.0.0.1355-f3c5da8 ; 5.0.4.1735-63db1b3 ; 4.0.7.3237-c6d4331 ; 3.0.14.33828-25cd017
    Checked on 6.0.0.1357-d37c931 ; 5.0.4.1735-0-5ee71b6 ; 4.0.7.3237-cdd12070 ; 3.0.14.33829-bd28d83
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation

#############
FLD_LEN = 500
TXT_PAD = 'QWERTY'
TXT_DATA = TXT_PAD * (FLD_LEN // len(TXT_PAD))
#############

db = db_factory(page_size = 8192)
substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

custom_tpb = tpb(isolation = Isolation.READ_COMMITTED, lock_timeout = -1)

#-----------------------------------------------------------

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):

    with act.db.connect() as con1, act.db.connect() as con2:
        con1.execute_immediate(f'create table t1 (id integer, str1 varchar(50), str2 varchar({FLD_LEN}))')
        con1.commit()
        con1.execute_immediate(f"insert into t1(id, str1, str2) values( 0, NULL, '{TXT_DATA}')")
        con1.commit()

        tx1 = con1.transaction_manager(custom_tpb)
        cur1 = tx1.cursor()
        cur1.execute('select * from t1')
        for r in cur1:
            pass

        con2.execute_immediate("update t1 set id = 1")
        con2.commit()
        con2.execute_immediate("alter table t1 drop str1")
        con2.commit()
        tx2 = con2.transaction_manager(custom_tpb)
        cur2 = tx2.cursor()
        cur2.execute('select * from t1 with lock');
        for r in cur2:
            pass

        cur1.execute('select * from t1')
        hdr=cur1.description
        for r in cur1:
            for i in range(0,len(hdr)):
                print( hdr[i][0].ljust(32),':', r[i] )

    act.expected_stdout = f"""
        ID   : 1
        STR1 : None
        STR2 : {TXT_DATA}
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
