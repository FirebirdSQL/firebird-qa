#coding:utf-8

"""
ID:          issue-7962
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7962
TITLE:       System procedure/function inconsistency between ISQL SHOW FUNCTIONS and SHOW PROCEDURES
NOTES:
    [23.01.2024] pzotov
    Confirmed on 6.0.0.219
    Checked on 6.0.0.219 after commit https://github.com/FirebirdSQL/firebird/commit/bcc53d43c8cd0b904d2963173c153056f9465a09
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create function standalone_fn() returns integer as begin return 1; end
    ^
    create procedure standalone_sp() as begin end
    ^
    create or alter package pg_test
    as
    begin
       function fn_user() returns int;
       procedure sp_user() returns (o int);
    end^
    set term ;^
    show functions;
    show procedure;
"""

act = isql_act('db', test_script)

expected_stdout = """
    STANDALONE_FN
    PG_TEST.FN_USER
    STANDALONE_SP
    PG_TEST.SP_USER
"""

@pytest.mark.version('>=5.0.1')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
