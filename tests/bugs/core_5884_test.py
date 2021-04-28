#coding:utf-8
#
# id:           bugs.core_5884
# title:        Initial global mapping from srp plugin does not work
# decription:   
#                  Confirmed bug on: 3.0.4.33020, 4.0.0.1143 ('TEST2' was shown instead of 'GTOST').
#                  Checked on:
#                    FB30SS, build 3.0.4.33021: OK, 2.312s.
#                
# tracker_id:   CORE-5884
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
    create or alter user tmp$c5884_1 password '123' using plugin Srp;
    create or alter user tmp$c5884_2 password '456' using plugin Srp;
    commit;

    create or alter mapping lmap using plugin srp from user tmp$c5884_1 to user ltost;
    create or alter global mapping gmap using plugin srp from user tmp$c5884_2 to user gtost; 
    commit;

    connect '$(DSN)' user tmp$c5884_1 password '123';
    select current_user as whoami from rdb$database;
    commit;

    connect '$(DSN)' user tmp$c5884_2 password '456';
    select current_user as whoami from rdb$database;
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    commit;


    drop global mapping gmap;
    drop mapping lmap;
    commit;

    drop user tmp$c5884_1 using plugin Srp;
    drop user tmp$c5884_2 using plugin Srp;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHOAMI                          LTOST
    WHOAMI                          GTOST
  """

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

