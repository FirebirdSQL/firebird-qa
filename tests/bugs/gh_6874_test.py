#coding:utf-8
#
# id:           bugs.gh_6874
# title:        Literal 65536 (interpreted as int) can not be multiplied by itself w/o cast if result more than 2^63-1
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6874
#               
#                   Confirmed need to explicitly cast literal 65536 on: 5.0.0.88, 4.0.1.2523 (otherwise get SQLSTATE = 22003).
#                   Checked on: 5.0.0.113, 4.0.1.2539 -- all OK.
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!sqltype:|multiply_result).)*$', ''), ('[ \t]+', ' '), ('.*alias:.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set sqlda_display on;
    select 65536*65536*65536*65536 as "multiply_result_1" from rdb$database;
    select -65536*-65536*-65536*-65536 as "multiply_result_2" from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    multiply_result_1                18446744073709551616

    01: sqltype: 32752 INT128 scale: 0 subtype: 0 len: 16
    multiply_result_2                18446744073709551616
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
