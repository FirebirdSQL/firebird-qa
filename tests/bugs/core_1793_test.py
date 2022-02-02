#coding:utf-8

"""
ID:          issue-2219
ISSUE:       2219
TITLE:       AV at prepare of query with unused parametrized CTE
DESCRIPTION:
JIRA:        CORE-1793
FBTEST:      bugs.core_1793
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Updated 06.01.2018:
    --  25SC, build 2.5.8.27089: OK, 0.297s.
    --  30SS, build 3.0.3.32861: OK, 1.578s.
    --  40SS, build 4.0.0.840: OK, 1.390s.
    recreate table test(x int);
    commit;
    set planonly;
    with
        x as (select x.x from test x),
        y as (select y.x from test y)
    select * from y;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (Y Y NATURAL)
"""

expected_stderr = """
    SQL warning code = -104
    -CTE "X" is not used in query
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

