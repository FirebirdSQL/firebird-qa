#coding:utf-8

"""
ID:          issue-4603
ISSUE:       4603
TITLE:       FB3: Stored function accepts duplicate input arguments
DESCRIPTION:
JIRA:        CORE-4280
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create view v_check as
    select
        rf.rdb$function_name as func_name
       ,rf.rdb$legacy_flag as legacy_flag
    from rdb$functions rf where rf.rdb$function_name = upper('psql_func_test')
    ;
    commit;

    set term ^;
    create function psql_func_test(x integer, y boolean, x integer) -- argument `x` appears twice
    returns integer as
    begin
        return x + 1;
    end
    ^
    set term ;^
    commit;

    set list on;
    set count on;
    select * from v_check;

"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 0
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    CREATE FUNCTION PSQL_FUNC_TEST failed
    -SQL error code = -901
    -duplicate specification of X - not supported
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

