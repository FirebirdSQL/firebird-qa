#coding:utf-8

"""
ID:          issue-5590
ISSUE:       5590
TITLE:       Data type unknown error with LIST
DESCRIPTION:
JIRA:        CORE-5313
FBTEST:      bugs.core_5313
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    set sqlda_display on;
    select list(trim(rdb$relation_name), ?) from rdb$relations;
"""

act = isql_act('db', test_script)

expected_stdout = """
    INPUT message field count: 1
    01: sqltype: 452 TEXT scale: 0 subtype: 0 len: 4 charset: 4 UTF8
      :  name:   alias:
      : table:   owner:

    PLAN (RDB$RELATIONS NATURAL)

    OUTPUT message field count: 1
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
      :  name: LIST  alias: LIST
      : table:   owner:
"""

# version: 3.0

@pytest.mark.version('>=3.0.1,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(charset='utf8')
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

