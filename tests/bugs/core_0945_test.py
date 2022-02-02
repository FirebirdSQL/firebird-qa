#coding:utf-8

"""
ID:          issue-1346
ISSUE:       1346
TITLE:       Bad error message when tring to create FK to non-existent table
DESCRIPTION:
JIRA:        CORE-945
FBTEST:      bugs.core_0945
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE TAB_TestA (
  UID INTEGER NOT NULL PRIMARY KEY
);

CREATE TABLE TAB_TestB (
  UID INTEGER NOT NULL PRIMARY KEY,
  TestA INTEGER CONSTRAINT FK_TestA REFERENCES TABTestA(UID) ON UPDATE CASCADE
);

"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE TAB_TESTB failed
-Table TABTESTA not found
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

