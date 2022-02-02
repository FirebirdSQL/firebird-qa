#coding:utf-8

"""
ID:          issue-4901
ISSUE:       4901
TITLE:       Can't create column check constraint when the column is domain based
DESCRIPTION:
JIRA:        CORE-4585
FBTEST:      bugs.core_4585
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create domain x int;
    create table test(
        x x constraint test_x_chk check(x>0)
    );
    insert into test(x) values(1);
    insert into test(x) values(0);
    set list on;
    select * from test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    X                               1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    Operation violates CHECK constraint TEST_X_CHK on view or table TEST
    -At trigger 'CHECK_1'
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

