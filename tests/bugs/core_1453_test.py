#coding:utf-8
#
# id:           bugs.core_1453
# title:        Allow usage of functions in LIST delimiter parameter
# decription:   
# tracker_id:   CORE-1443
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (ID INTEGER, NAME CHAR(20));
COMMIT;
INSERT INTO T1 (ID,NAME) VALUES (1,'ORANGE');
INSERT INTO T1 (ID,NAME) VALUES (1,'APPLE');
INSERT INTO T1 (ID,NAME) VALUES (1,'LEMON');
INSERT INTO T1 (ID,NAME) VALUES (2,'ORANGE');
INSERT INTO T1 (ID,NAME) VALUES (2,'APPLE');
INSERT INTO T1 (ID,NAME) VALUES (2,'PEAR');
COMMIT;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select ID,  LIST( trim(NAME), ASCII_CHAR(35) )
from T1
group by 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_1453.fdb, User: SYSDBA
SQL> CON> CON>
          ID              LIST
============ =================
           1               0:1
==============================================================================
LIST:
ORANGE#LEMON#APPLE
==============================================================================
           2               0:2
==============================================================================
LIST:
PEAR#ORANGE#APPLE
==============================================================================

SQL>"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

