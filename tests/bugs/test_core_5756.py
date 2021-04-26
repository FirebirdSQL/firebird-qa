#coding:utf-8
#
# id:           bugs.core_5756
# title:        Regression: FB crashes when trying to recreate table that is in use by DML (3.0.3; 3.0.4; 4.0.0)
# decription:   
#                  Detected bug on 3.0.4.32819 and 4.0.0.853. 
#                  Checked on:
#                      3.0.4.32920: OK, 1.047s.
#                      4.0.0.912: OK, 1.188s.
#                
# tracker_id:   CORE-5756
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test(x int);
    insert into test values(1);
    select * from test;
    recreate table test(x int, y int); -- this led to crash
    commit;
    select * from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
    X                               1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -object TABLE "TEST" is in use
  """

@pytest.mark.version('>=3.0.4')
def test_core_5756_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

