#coding:utf-8

"""
ID:          issue-6142
ISSUE:       6142
TITLE:       Initial global mapping from srp plugin does not work
DESCRIPTION:
JIRA:        CORE-5884
"""

import pytest
from firebird.qa import *

db = db_factory()

user_a = user_factory('db', name='tmp$c5884_1', password='123', plugin='Srp')
user_b = user_factory('db', name='tmp$c5884_2', password='456', plugin='Srp')

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    WHOAMI                          LTOST
    WHOAMI                          GTOST
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action, user_a: User, user_b: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
