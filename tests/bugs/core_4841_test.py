#coding:utf-8
#
# id:           bugs.core_4841
# title:        Make message about missing password being always displayed as reply on attempt to issue CREATE new login without PASSWORD clause
# decription:
#                   Checked on
#                       4.0.0.2271 SS; 4.0.0.2265 SS; 4.0.0.2267 CS.
#                       3.0.8.33392 SS; 3.0.8.33390 SC; 3.0.7.33388 CS.
#
# tracker_id:   CORE-4841
# min_versions: ['3.0.7']
# versions:     3.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.7
# resources: None

substitutions_1 = [('[-]?Password', 'Password')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- All following statements must fail with message that contains phrase:
    -- "Password must be specified when creating user"
    create user u01;
    create user u01 using plugin Srp;
    create user u01 firstname 'john';
    create user u01 grant admin role;
    create user u01 inactive;
    create or alter user u01 tags (password = 'foo');
    create user password;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE USER U01 failed
-Password must be specified when creating user
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE USER U01 failed
-Password must be specified when creating user
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE USER U01 failed
-Password must be specified when creating user
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE USER U01 failed
-Password must be specified when creating user
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE USER U01 failed
-Password must be specified when creating user
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE USER PASSWORD failed
-Password must be specified when creating user
"""

@pytest.mark.version('>=3.0.7')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

