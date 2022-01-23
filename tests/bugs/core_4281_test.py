#coding:utf-8

"""
ID:          issue-4604
ISSUE:       4604
TITLE:       FB 3: TYPE OF arguments of stored functions will hang firebird engine if depending domain or column is changed
DESCRIPTION:
JIRA:        CORE-4281
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create domain testdomain as integer;
    commit;

    create function testfunction (arg1 type of testdomain) returns integer as
    begin
    end;

    commit;
    alter domain testdomain type bigint;
    commit;

    show domain testdomain;
"""

act = isql_act('db', test_script)

expected_stdout = """
    TESTDOMAIN                      BIGINT Nullable
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
