#coding:utf-8

"""
ID:          issue-4483
ISSUE:       4483
TITLE:       RDB$GET_CONTEXT/RDB$SET_CONTEXT parameters incorrectly described as CHAR NOT NULL instead of VARCHAR NULLABLE
DESCRIPTION:
JIRA:        CORE-4156
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    set sqlda_display on;
    select rdb$set_context( ?, ?, ?) x from rdb$database;
    -- NB: output in 3.0 will contain values of sqltype with ZERO in bit_0,
    -- so it will be: 448 instead of previous 449, and 496 instead of 497.
    -- Result is value that equal to constant from src/dsql/sqlda_pub.h, i.e:
    -- #define SQL_VARYING 448
    -- #define SQL_LONG    496
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')])

expected_stdout = """
    01: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 80 charset: 0 NONE
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 80 charset: 0 NONE
    03: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 255 charset: 0 NONE
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

