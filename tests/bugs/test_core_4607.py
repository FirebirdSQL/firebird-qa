#coding:utf-8
#
# id:           bugs.core_4607
# title:        Add support for having more than one UserManager in firebird.conf and use them from SQL
# decription:   
#                  Line "UserManager = Srp,..." has been added since ~MAR-2018 in firebird.conf before every fbt_run launch.
#                  Initial attempt to use Srp failed for following COREs tests: 2307, 3365, 4200, 4301, 4469 - and error
#                  was the same for all of them:
#                  ===
#                     -Install incomplete, please read chapter "Initializing security
#                     database" in Quick Start Guide
#                  ===
#                  (reply from dimitr, letter 31.05.2015 17:44).
#               
#                  Checked on:
#                       fb30Cs, build 3.0.4.32972: OK, 0.844s.
#                       FB30SS, build 3.0.4.32988: OK, 1.203s.
#                       FB40CS, build 4.0.0.955: OK, 2.016s.
#                       FB40SS, build 4.0.0.1008: OK, 1.328s.
#                
# tracker_id:   CORE-4607
# min_versions: ['3.0.0']
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
    set list on;
    set count on;
    create view v_test as
    select sec$user_name, sec$plugin
    from sec$users 
    where upper(sec$user_name) starting with upper('tmp$c4607')
    order by 1,2
    ;
    commit;
    create or alter user tmp$c4607_leg password '123' using plugin Legacy_UserManager;
    create or alter user tmp$c4607_srp password '456' using plugin Srp;
    commit;
    select * from v_test;
    commit;
    drop user tmp$c4607_leg using plugin Legacy_UserManager;
    drop user tmp$c4607_srp using plugin Srp;
    commit;
    select * from v_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SEC$USER_NAME                   TMP$C4607_LEG
    SEC$PLUGIN                      Legacy_UserManager

    SEC$USER_NAME                   TMP$C4607_SRP
    SEC$PLUGIN                      Srp

    Records affected: 2

    Records affected: 0
  """

@pytest.mark.version('>=3.0')
def test_core_4607_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

