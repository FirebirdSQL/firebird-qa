#coding:utf-8

"""
ID:          issue-4889
ISSUE:       4889
TITLE:       Incorrect error for PSQL function when the number of actual arguments does
  not match the number of formal arguments
DESCRIPTION:
JIRA:        CORE-4572
FBTEST:      bugs.core_4572
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter function fn_multiplier ( a_val int, a_times int ) returns bigint
    as
    begin
        return a_val * a_times;
    end
    ^

    create or alter procedure sp_multiplier (a_val int, a_times int )
    returns (result bigint)
    as
    begin
        result = a_val * a_times;
    end
    ^
    set term ;^
    commit;

    -- Confirmed on WI-T3.0.0.31374 Firebird 3.0 Beta 1:
    -- Statement failed, SQLSTATE = 39000
    -- invalid request BLR at offset 50
    -- -function FN_MULTIPLIER could not be matched
    select fn_multiplier(191) as t from rdb$database;

    execute procedure sp_multiplier(191);
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 07001
    Dynamic SQL Error
    -Input parameter mismatch for function FN_MULTIPLIER

    Statement failed, SQLSTATE = 07001
    Dynamic SQL Error
    -Input parameter mismatch for procedure SP_MULTIPLIER
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

