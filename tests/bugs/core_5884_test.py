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
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

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
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHOAMI                          TMP$C5884_1
    WHOAMI                          TMP$C5884_2
"""

user_1a = user_factory('db_1', name='tmp$c5884_1', password='123', plugin='Srp')
user_1b = user_factory('db_1', name='tmp$c5884_2', password='456', plugin='Srp')

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action, user_1a: User, user_1b: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    # [pcisar]
    # 3.11.2021 This test fails for 3.0.8/4.0 (returns tmp$ user names instead mapped ones)
    assert act_1.clean_stdout == act_1.clean_expected_stdout

