#coding:utf-8

"""
ID:          new-database-01
TITLE:       New DB - RDB$DATABASE content
DESCRIPTION: Check the correct content of RDB$DATABASE in new database.
FBTEST:      functional.basic.db.01
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set blob all;
    select * from rdb$database;
"""

act = isql_act('db', test_script, substitutions=[('RDB\\$SECURITY_CLASS[ ]+SQL\\$.*', '')])

# version: 3.0

expected_stdout = """
    RDB$DESCRIPTION                 <null>
    RDB$RELATION_ID                 128
    RDB$SECURITY_CLASS              SQL$362
    RDB$CHARACTER_SET_NAME          NONE
    RDB$LINGER                      <null>
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """
    RDB$DESCRIPTION                 <null>
    RDB$RELATION_ID                 128
    RDB$SECURITY_CLASS              SQL$362
    RDB$CHARACTER_SET_NAME          NONE
    RDB$LINGER                      <null>
    RDB$SQL_SECURITY                <null>
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
