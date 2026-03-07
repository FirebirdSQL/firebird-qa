#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8933
TITLE:       Isql SHOW PROCEDURE/FUNCTION doesn't show NOT NULL status for parameters
DESCRIPTION:
NOTES:
    [08.03.2026] pzotov
    Additional substitutions are used in order to filter out messages that no relevant to this test purpose.
    Confirmed bug on 6.0.0.1808-0acd6e0.
    Checked on 6.0.0.1811-89ef46f.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter procedure pn (
        sp_inp_nullable int,
        sp_inp_not_null int not null
    ) returns(
        sp_out_nullable int,
        sp_out_not_null int not null
    )
    as 
    begin
        exit;
    end
    ^
    create or alter function fn1 (
        fn_inp_nullable int,
        fn_inp_not_null int not null
    ) returns int as 
    begin
        return 1;
    end
    ^

    create or alter function fn2 returns int not null as 
    begin
        return 1;
    end
    ^

    set term ;^
    commit;
    show procedure pn;
    show function fn1;
    show function fn2;
"""

substitutions = [('^((?!(SP_INP_|SP_OUT_|FN_INP_|OUTPUT)).)*$', ''), ('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    SP_INP_NULLABLE INPUT INTEGER
    SP_INP_NOT_NULL INPUT INTEGER NOT NULL
    SP_OUT_NULLABLE OUTPUT INTEGER
    SP_OUT_NOT_NULL OUTPUT INTEGER NOT NULL
    OUTPUT INTEGER
    FN_INP_NULLABLE INPUT INTEGER
    FN_INP_NOT_NULL INPUT INTEGER NOT NULL
    OUTPUT INTEGER NOT NULL
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
