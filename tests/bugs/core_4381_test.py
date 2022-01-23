#coding:utf-8

"""
ID:          issue-4703
ISSUE:       4703
TITLE:       Incorrect line/column information in runtime errors
DESCRIPTION:
JIRA:        CORE-4381
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
set term ^;



create or alter procedure p1 returns (x integer) as
begin
                           select
                                                 'a'
                           from rdb$database
                                             into x;
end
^

execute procedure p1
^
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "a"
    -At procedure 'P1' line: 3, col: 28
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

