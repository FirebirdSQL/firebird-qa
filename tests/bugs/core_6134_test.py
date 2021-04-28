#coding:utf-8
#
# id:           bugs.core_6134
# title:         Win_Sspi in the list of auth plugins leads message about failed login to be changed (from 'Your user name and password are not defined...' to 'Missing security context ...')
# decription:   
#                   Test assumes that firebird.conf parameter AuthClient is: Legacy_Auth,Srp,Win_Sspi.
#                   This is done automaticaally by script that is launched daily on Firebird test machine.
#                   Checked on: 4.0.0.1598, WI-V3.0.5.33168 -- all fine.
#                
# tracker_id:   CORE-6134
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
     set heading off;
     set term ^;
     execute block returns (whoami varchar(32)) as 
     begin 
         execute statement 'select current_user from rdb$database' 
             as user 'SYSDBA' 
             password 'ful1yWr0ng'  -- or use here some other password that is for sure invalid
         into whoami; 
         suspend; 
     end
     ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
  """

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

