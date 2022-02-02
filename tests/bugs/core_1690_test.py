#coding:utf-8

"""
ID:          issue-2116
ISSUE:       2116
TITLE:       Arithmetic exception, numeric overflow, or string truncation in utf8 tables
DESCRIPTION:
JIRA:        CORE-1690
FBTEST:      bugs.core_1690
"""

import pytest
from firebird.qa import *

init_script = """create table A (C1 INTEGER PRIMARY KEY);
"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """show table A;
"""

act = isql_act('db', test_script)

expected_stdout = """C1                              INTEGER Not Null
CONSTRAINT INTEG_2:
  Primary key (C1)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

