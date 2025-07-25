#coding:utf-8

"""
ID:          issue-3672
ISSUE:       3672
TITLE:       "BLOB not found" error after creation/altering of the invalid trigger
DESCRIPTION:
JIRA:        CORE-3305
FBTEST:      bugs.core_3305
NOTES:
    [27.06.2025] pzotov
    Reimplemented: make single test function for the whole code, use different variables to store output on 3.x / 4.x+5.x / 6.x
    No substitutions are used to suppress schema and quotes. Discussed with dimitr, 24.06.2025 12:39.

    Checked on 6.0.0.876; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(v int);
    set term ^;
    create or alter trigger test_ai for test active AFTER insert position 0 as
    begin
        new.v = 1;
    end
    ^
    set term ;^
    insert into test(v) values(123);
    rollback;
"""

act = isql_act('db', test_script)

expected_out_3x = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column
"""

expected_out_5x = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column TEST.V
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column TEST.V
"""

expected_out_6x = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column "PUBLIC"."TEST"."V"
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column "PUBLIC"."TEST"."V"
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_out_3x if act.is_version('<4') else expected_out_5x if act.is_version('<6') else expected_out_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
