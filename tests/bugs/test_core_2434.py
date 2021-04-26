#coding:utf-8
#
# id:           bugs.core_2434
# title:        CREATE USER command: Invalid error message
# decription:   Attempt to create user with empty password should raise error with message related to this problem
# tracker_id:   CORE-2434
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create user tmp$c2434 password '';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE USER TMP$C2434 failed
    -Password should not be empty string
  """

@pytest.mark.version('>=3.0')
def test_core_2434_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

