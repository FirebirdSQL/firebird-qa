#coding:utf-8

"""
ID:          issue-5653
ISSUE:       5653
TITLE:       Allow subroutines to call others subroutines and themself recursively
DESCRIPTION:
  We check not only ability of recursive calls but also max depth of them. It should be equal to 1000.
JIRA:        CORE-5380
FBTEST:      bugs.core_5380
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter function get_arithmetic_progression_total(n smallint) returns decfloat(34)  as
        declare function get_sub_total_recursively(n smallint) returns decfloat(34) as
        begin
            if (n = 1) then
                return 1;
            else
                return n + get_sub_total_recursively(n - 1);
        end
    begin
        if (n <= 0) then
            return 0;
        else
            return get_sub_total_recursively(n);
    end
    ^
    set term ;^
    commit;

    set list on;
    select get_arithmetic_progression_total(1001) as arithmetic_progression_total from rdb$database;
    select get_arithmetic_progression_total(1002) as arithmetic_progression_total from rdb$database;
    -- (a1 + an) * n / 2
"""

act = isql_act('db', test_script, substitutions=[('line:\\s[0-9]+,', 'line: x'),
                                                 ('col:\\s[0-9]+', 'col: y')])

expected_stdout = """
    ARITHMETIC_PROGRESSION_TOTAL                                        501501
"""

expected_stderr = """
    Statement failed, SQLSTATE = 54001
    Too many concurrent executions of the same request
    -At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY' line: 7, col: 13
    At sub function 'GET_SUB_TOTAL_RECURSIVELY'...
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

