#coding:utf-8
#
# id:           functional.role.create.01
# title:        CREATE ROLE
# decription:   
#                   CREATE ROLE
#                   Dependencies:
#                   CREATE DATABASE
#                   Basic SELECT
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     3.0, 4.0
# qmid:         functional.role.create.create_role_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('SQL\\$.*', 'SQLnnnn')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create role test;
    commit;
    set list on;
    select * from rdb$roles order by rdb$role_name;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$SECURITY_CLASS              SQLnnnn
    
    RDB$ROLE_NAME                   TEST
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 0
    RDB$SECURITY_CLASS              SQLnnnn
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = [('SQL\\$.*', 'SQLnnnn')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    create role test;
    commit;
    set list on;
    select * from rdb$roles order by rdb$role_name;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$SECURITY_CLASS              SQLnnnn
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF

    RDB$ROLE_NAME                   TEST
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 0
    RDB$SECURITY_CLASS              SQLnnnn
    RDB$SYSTEM_PRIVILEGES           0000000000000000
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

