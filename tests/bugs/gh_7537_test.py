#coding:utf-8

"""
ID:          issue-7537
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7537
TITLE:       Wrong name in error message when unknown namespace is passed into RDB$SET_CONTEXT()
NOTES:
    [03.04.2023] pzotov
    Checked on intermediate snapshots 4.0.3.2920, 5.0.0.1001.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    select rdb$set_context('NS', 'VARNAME', 2) from rdb$database;
    select rdb$set_context('', 'VARNAME', 2) from rdb$database;
    select rdb$set_context('FOO', '', 2) from rdb$database;

    select rdb$get_context('NS', 'VARNAME') from rdb$database;
    select rdb$get_context('', 'VARNAME') from rdb$database;
    select rdb$get_context('FOO', '') from rdb$database;
"""

expected_stdout = """
    Statement failed, SQLSTATE = HY000
    Invalid namespace name NS passed to RDB$SET_CONTEXT

    Statement failed, SQLSTATE = HY000
    Invalid namespace name  passed to RDB$SET_CONTEXT

    Statement failed, SQLSTATE = HY000
    Invalid namespace name FOO passed to RDB$SET_CONTEXT

    Statement failed, SQLSTATE = HY000
    Invalid namespace name NS passed to RDB$GET_CONTEXT

    Statement failed, SQLSTATE = HY000
    Invalid namespace name  passed to RDB$GET_CONTEXT

    Statement failed, SQLSTATE = HY000
    Invalid namespace name FOO passed to RDB$GET_CONTEXT
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3.0.11')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
