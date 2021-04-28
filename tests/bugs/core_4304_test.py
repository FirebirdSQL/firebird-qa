#coding:utf-8
#
# id:           bugs.core_4304
# title:        Engine crashes when attempt to REcreate table with FK after syntax error before such recreating
# decription:   
# tracker_id:   CORE-4304
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='NONE', sql_dialect=3, init=init_script_1)

test_script_1 = """
recreate table t1(x int);
recreate table t1(x int, constraint t1_pk primary key(x), y int, constraint t1_fk foreign key(y) references t1(z)); -- NB: there is no field `z` in this table, this was misprit
recreate table t1(x int, constraint t1_pk primary key(x), y int, constraint t1_fk foreign key(y) references t1(x));
commit;
show table t1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
X                               INTEGER Not Null
Y                               INTEGER Nullable
CONSTRAINT T1_FK:
  Foreign key (Y)    References T1 (X)
CONSTRAINT T1_PK:
  Primary key (X)
  """
expected_stderr_1 = """
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-RECREATE TABLE T1 failed
-could not find UNIQUE or PRIMARY KEY constraint in table T1 with specified columns
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

