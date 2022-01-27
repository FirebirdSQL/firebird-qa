#coding:utf-8

"""
ID:          issue-6578
ISSUE:       6578
TITLE:       SubType information is lost when calculating arithmetic expressions
DESCRIPTION:
NOTES:
[25.06.2020]
  4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
JIRA:        CORE-6337
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display on;
    set list on;
    select cast(1 as numeric(18,2)) * cast(1 as numeric(18,2)) from rdb$database;
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype).)*$', ''), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 32752 INT128 scale: -4 subtype: 1 len: 16
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
