#coding:utf-8

"""
ID:          issue-4906
ISSUE:       4906
TITLE:       Change type of returning value of CHAR_LENGTH, BIT_LENGTH and OCTET_LENGTH of BLOBs to bigint
DESCRIPTION:
JIRA:        CORE-4590
FBTEST:      bugs.core_4590
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display;
    set planonly;
    select
        char_length(rdb$description) clen
        ,bit_length(rdb$description) blen
        ,octet_length(rdb$description) olen
    from rdb$database;
    -- No more output of charset name for NON-text field, see:
    -- http://sourceforge.net/p/firebird/code/61779 // 10.06.2015
    -- Enhance metadata display - show charset only for fields where it makes sense
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')])

expected_stdout = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

