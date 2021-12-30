#coding:utf-8
#
# id:           bugs.gh_6845
# title:        Result type of AVG over BIGINT column results in type INT128
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6845
#               
#                   Confirmed ticket issue on 5.0.0.88 and 4.0.1.2523.
#                   Checked on: 5.0.0.114, 4.0.1.2540 -- all OK.
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
    recreate table test(x bigint, y decfloat(16));

    set sqlda_display on;
    set list on;
    select avg(x) as avg_bigint, avg(y) as avg_decf16 from test having false;
    select avg(x)over() as avg_bigint_over, avg(y)over() as avg_decf16_over from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 32760 DECFLOAT(16) Nullable scale: 0 subtype: 0 len: 8

    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 32760 DECFLOAT(16) Nullable scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
