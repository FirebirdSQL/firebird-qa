#coding:utf-8

"""
ID:          issue-2041
ISSUE:       2041
TITLE:       Incorrect error message (column number) if the empty SQL string is prepared
DESCRIPTION:
JIRA:        CORE-1620
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create procedure test_es1 as
    begin
        execute statement '';
    end
    ^
    set term ;^
    commit;
    execute procedure test_es1;
"""

act = isql_act('db', test_script, substitutions=[("-At procedure 'TEST_ES1' line:.*", '')])

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Unexpected end of command - line 1, column 1
    -At procedure 'TEST_ES1' line: 3, col: 9
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

