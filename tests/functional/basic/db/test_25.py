#coding:utf-8

"""
ID:          new-database-25
TITLE:       New DB - RDB$ROLES content
DESCRIPTION: Check the correct content of RDB$ROLES in new database.
FBTEST:      functional.basic.db.25
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    -- NB: rdb$role_name is UNIQUE column.
    select * from rdb$roles order by rdb$role_name;
"""

act = isql_act('db', test_script,
               substitutions=[('RDB\\$SECURITY_CLASS\\s+SQL.*', 'RDB\\$SECURITY_CLASS SQL'),
                              ('[\t ]+', ' ')])

# version: 3.0

expected_stdout_1 = """
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB$OWNER_NAME                  SYSDBA
    RDB$DESCRIPTION                 <null>
    RDB$SYSTEM_FLAG                 1
    RDB$SECURITY_CLASS              SQL$162

    Records affected: 1
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

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
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
