#coding:utf-8
#
# id:           bugs.core_5423
# title:        Regression: "Invalid usage of boolean expression" when use "BETWEEN" and "IS" operators
# decription:   
#                
# tracker_id:   CORE-5423
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '-At line: column:')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select 1 k from rdb$database where 1 between 0 and 2 and null is null;
    select 2 k from rdb$database where 1 between 0 and 2 and foo is not null;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    K                               1


    Records affected: 1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -FOO
    -At line: column:
  """

@pytest.mark.version('>=3.0')
def test_core_5423_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

