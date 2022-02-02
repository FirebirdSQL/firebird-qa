#coding:utf-8

"""
ID:          issue-6113
ISSUE:       6113
TITLE:       Forward-compatible expressions LOCALTIME and LOCALTIMESTAMP
DESCRIPTION:
JIRA:        CORE-5853
FBTEST:      bugs.core_5853
"""

import pytest
from firebird.qa import *

db = db_factory()

# version: 3.0

test_script_1 = """
    set planonly;
    select current_time, current_timestamp from rdb$database;
    select localtime from rdb$database;
    select localtimestamp from rdb$database;
"""

act_1 = isql_act('db', test_script_1)

expected_stdout_1 = """
    PLAN (RDB$DATABASE NATURAL)
    PLAN (RDB$DATABASE NATURAL)
    PLAN (RDB$DATABASE NATURAL)
"""

@pytest.mark.version('>=2.5.9,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0

test_script_2 = """
    set planonly;
    select current_time, current_timestamp from rdb$database;
    --select localtime from rdb$database;
    --select localtimestamp from rdb$database;
"""

act_2 = isql_act('db', test_script_2)

expected_stdout_2 = """
    PLAN (RDB$DATABASE NATURAL)
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout
