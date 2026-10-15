#coding:utf-8

"""
ID:          issue-2991
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/2991
TITLE:       Infinity should not escape from the engine (client side tools should not see the special values)
DESCRIPTION:
JIRA:        CORE-2581
NOTES:
    [15.10.2026] pzotov
    Fixed misspelling: no space was between `1e-161` and `from`.
    This causes parsing error in 6x (SQLSTATE = 42000 / Token unknown / -1e-161from)
    since  #afba279 New feature non-decimal integer literals (SQL:2023 T661)

    Checked on 6.0.0.2211; 5.0.5.1906; 4.0.8.3328; 3.0.15.33890
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail OFF;
    set wng off;
    set list on;

    set sql dialect 1;
    select 1e161 / 1e-161 from rdb$database;

    set sql dialect 3;
    select 1e308 + 1e308 from rdb$database;
    select 1e308 - -1e308 from rdb$database;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Statement failed, SQLSTATE = 22003
    arithmetic exception, numeric overflow, or string truncation
    -Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

    Statement failed, SQLSTATE = 22003
    arithmetic exception, numeric overflow, or string truncation
    -Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

    Statement failed, SQLSTATE = 22003
    arithmetic exception, numeric overflow, or string truncation
    -Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
