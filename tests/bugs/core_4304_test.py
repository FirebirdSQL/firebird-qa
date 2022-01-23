#coding:utf-8

"""
ID:          issue-4627
ISSUE:       4627
TITLE:       Engine crashes when attempt to REcreate table with FK after syntax error before such recreating
DESCRIPTION:
JIRA:        CORE-4304
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
recreate table t1(x int);
recreate table t1(x int, constraint t1_pk primary key(x), y int, constraint t1_fk foreign key(y) references t1(z)); -- NB: there is no field `z` in this table, this was misprit
recreate table t1(x int, constraint t1_pk primary key(x), y int, constraint t1_fk foreign key(y) references t1(x));
commit;
show table t1;
"""

act = isql_act('db', test_script)

expected_stdout = """
X                               INTEGER Not Null
Y                               INTEGER Nullable
CONSTRAINT T1_FK:
  Foreign key (Y)    References T1 (X)
CONSTRAINT T1_PK:
  Primary key (X)
"""

expected_stderr = """
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-RECREATE TABLE T1 failed
-could not find UNIQUE or PRIMARY KEY constraint in table T1 with specified columns
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

