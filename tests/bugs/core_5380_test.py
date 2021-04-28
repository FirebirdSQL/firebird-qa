#coding:utf-8
#
# id:           bugs.core_5380
# title:        Allow subroutines to call others subroutines and themself recursively
# decription:   
#                    We check not only ability of recursive calls but also max depth of them. It should be equal to 1000.
#                    FB40SS, build 4.0.0.688: OK, 0.890s.
#                
# tracker_id:   CORE-5380
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('line:\\s[0-9]+,', 'line: x'), ('col:\\s[0-9]+', 'col: y')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ARITHMETIC_PROGRESSION_TOTAL                                        501501
  """
expected_stderr_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

