#coding:utf-8
#
# id:           functional.basic.db.25
# title:        Empty DB - RDB$ROLES
# decription:   Check for correct content of RDB$ROLES in empty database.
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_25

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$SECURITY_CLASS\\s+SQL.*', 'RDB\\$SECURITY_CLASS SQL'), ('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    -- NB: rdb$role_name is UNIQUE column.
    select * from rdb$roles order by rdb$role_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$SECURITY_CLASS              SQL$162

    Records affected: 1
  """

@pytest.mark.version('>=3.0,<4.0')
def test_25_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('RDB\\$SECURITY_CLASS\\s+SQL.*', 'RDB\\$SECURITY_CLASS SQL'), ('[\t ]+', ' ')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set count on;
    -- NB: rdb$role_name is UNIQUE column.
    select * from rdb$roles order by rdb$role_name;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$SECURITY_CLASS              SQL$383
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF

    Records affected: 1
  """

@pytest.mark.version('>=4.0')
def test_25_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

