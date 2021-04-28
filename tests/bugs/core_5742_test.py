#coding:utf-8
#
# id:           bugs.core_5742
# title:        Incorrect error message in iSQL when trying to create database with wrong password
# decription:   
#                    We can just attempt to create current test database with wrong password.
#                    Result should contain text "SQLSTATE=28000"
#                    ("Your user name and password are not defined" or "install incomplete..." - no matter).
#               
#                    Confirmed bug on 3.0.4.32917; 4.0.0.907
#                    Works fine on 3.0.4.32919.
#                
# tracker_id:   CORE-5742
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = [('^((?!SQLSTATE).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    commit;
    create database '$(DSN)' user sysdba password 'T0tAlly$Wr0ng';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
  """

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

