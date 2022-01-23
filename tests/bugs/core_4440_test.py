#coding:utf-8

"""
ID:          issue-4760
ISSUE:       4760
TITLE:       isql crash without connect when execute command "show version"
DESCRIPTION:
JIRA:        CORE-4440
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    show version;
    set list on;
    select current_user from rdb$database;
"""

act = isql_act('db', test_script, substitutions=[('^((?!SYSDBA).)*$', '')])

expected_stdout = """
    USER                            SYSDBA
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

