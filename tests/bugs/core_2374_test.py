#coding:utf-8

"""
ID:          issue-2796
ISSUE:       2796
TITLE:       ALTER TRIGGER / PROCEDURE wrong error message
DESCRIPTION:
JIRA:        CORE-2374
FBTEST:      bugs.core_2374
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    alter procedure test1 as
    begin
      if (a = b) then
       b = 1;
    end
    ^
    alter trigger trg1 as
    begin
      if (a = b) then
       b = 1;
    end
    ^
    set term ;^
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER PROCEDURE TEST1 failed
    -Procedure TEST1 not found
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TRIGGER TRG1 failed
    -Trigger TRG1 not found
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

