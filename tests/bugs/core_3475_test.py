#coding:utf-8

"""
ID:          issue-3836
ISSUE:       3836
TITLE:       Parameters inside the CAST function are described as not nullable
DESCRIPTION:
JIRA:        CORE-3475
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    set sqlda_display;
    select cast(null as int) v1, cast(? as int) v2 from rdb$database;
"""

act = isql_act('db', test_script,
                 substitutions=[('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')])

expected_stdout = """
    01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    02: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

