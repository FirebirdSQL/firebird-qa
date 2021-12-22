#coding:utf-8
#
# id:           bugs.core_4156
# title:        RDB$GET_CONTEXT/RDB$SET_CONTEXT parameters incorrectly described as CHAR NOT NULL instead of VARCHAR NULLABLE
# decription:   
# tracker_id:   CORE-4156
# min_versions: ['2.1.7']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    set sqlda_display on;
    select rdb$set_context( ?, ?, ?) x from rdb$database;
    -- NB: output in 3.0 will contain values of sqltype with ZERO in bit_0,
    -- so it will be: 448 instead of previous 449, and 496 instead of 497.
    -- Result is value that equal to constant from src/dsql/sqlda_pub.h, i.e:
    -- #define SQL_VARYING 448
    -- #define SQL_LONG    496
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 80 charset: 0 NONE
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 80 charset: 0 NONE
    03: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 255 charset: 0 NONE
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

