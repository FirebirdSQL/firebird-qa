#coding:utf-8
#
# id:           bugs.core_3000
# title:        Error on delete user "ADMIN"
# decription:   
#                  Also added sample from core-3110
#                
# tracker_id:   CORE-3000
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.7
# resources: None

substitutions_1 = [('-Token unknown - line.*', '-Token unknown')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Following users should NOT be created:
    create user 'ADMIN' password '123';
    create user 'CHECK' password '123';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown
    -'ADMIN'

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown
    -'CHECK'
  """

@pytest.mark.version('>=2.5.7')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

