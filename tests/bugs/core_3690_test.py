#coding:utf-8

"""
ID:          issue-4038
ISSUE:       4038
TITLE:       Wrong warning message for ambiguous query
DESCRIPTION: SQL dialect 1 allows such queries for backward compatibility reasons
JIRA:        CORE-3690
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    select m.mon$sql_dialect from mon$database m;
    select 0*rdb$relation_id as id from rdb$database,rdb$database;
"""

act = isql_act('db', test_script)

expected_stdout = """
    MON$SQL_DIALECT                 3
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42702
    Dynamic SQL Error
    -SQL error code = -204
    -Ambiguous field name between table RDB$DATABASE and table RDB$DATABASE
    -RDB$RELATION_ID
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

