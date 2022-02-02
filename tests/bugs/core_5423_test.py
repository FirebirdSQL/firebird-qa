#coding:utf-8

"""
ID:          issue-5695
ISSUE:       5695
TITLE:       Regression: "Invalid usage of boolean expression" when use "BETWEEN" and "IS" operators
DESCRIPTION:
JIRA:        CORE-5423
FBTEST:      bugs.core_5423
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    set count on;
    select 1 k from rdb$database where 1 between 0 and 2 and null is null;
    select 2 k from rdb$database where 1 between 0 and 2 and foo is not null;
"""

act = isql_act('db', test_script,
               substitutions=[('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+',
                               '-At line: column:')])

expected_stdout = """
    K                               1

    Records affected: 1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -FOO
    -At line: column:
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

