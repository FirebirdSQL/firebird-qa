#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8956
TITLE:       DECLARE VARIABLE does not accept arbitrary expressions within declared routines
DESCRIPTION:
NOTES:
    [26.03.2026] pzotov
    Confirmed problem on 6.0.0.1850-b8c5981
    Checked on 6.0.0.1858-c0190d0.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set autoterm on;
    set list on;
    execute block returns (eb_outcome int) as
        declare function f(x int) returns int
        as
            declare u int = x + 1;
            declare v int = u + 1;
            declare w int = v + u;
        begin
            return x + u + v + w;
        end

        declare g int = f(1) * f(2);
    begin
        eb_outcome = g;
        suspend;
    end;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    EB_OUTCOME 176
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
