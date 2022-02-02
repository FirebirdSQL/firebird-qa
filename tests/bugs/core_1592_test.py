#coding:utf-8

"""
ID:          issue-2013
ISSUE:       2013
TITLE:       Altering procedure parameters can lead to unrestorable database
DESCRIPTION:
JIRA:        CORE-1592
FBTEST:      bugs.core_1592
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    set term ^;
    create or alter procedure p2 as begin end
    ^
    commit
    ^
    create or alter procedure p1 returns ( x1 integer ) as begin
    x1 = 10; suspend;
    end
    ^
    create or alter procedure p2 returns ( x1 integer ) as begin
    for select x1 from p1 into :x1 do suspend;
    end
    ^

    -- This should FAIL and terminate script execution:
    alter procedure p1 returns ( x2 integer ) as begin
    x2 = 10; suspend;
    end
    ^
    set term ;^
    commit;

"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -PARAMETER P1.X1
    -there are 1 dependencies
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

