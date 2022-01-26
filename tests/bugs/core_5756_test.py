#coding:utf-8

"""
ID:          issue-6019-A
ISSUE:       6019
TITLE:       Regression: FB crashes when trying to recreate table that is in use by DML (3.0.3; 3.0.4; 4.0.0)
DESCRIPTION:
JIRA:        CORE-5756
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table test(x int);
    insert into test values(1);
    select * from test;
    recreate table test(x int, y int); -- this led to crash
    commit;
    select * from test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    X                               1
    X                               1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -object TABLE "TEST" is in use
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
