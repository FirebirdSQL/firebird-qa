#coding:utf-8

"""
ID:          issue-5804
ISSUE:       5804
TITLE:       Connections compressed and encrypted in MON$ATTACHMENTS table
DESCRIPTION:
JIRA:        CORE-5536
FBTEST:      bugs.core_5536
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    set sqlda_display on;
    select mon$wire_compressed, mon$wire_encrypted
    from mon$attachments
    where mon$attachment_id = current_connection
    ;
    -- Fields that were used before:
    -- MON$CONNECTION_COMPRESSED in (false, true)
    -- and MON$CONNECTION_ENCRYPTED in (false, true)
"""

act = isql_act('db', test_script)

expected_stdout = """
    INPUT message field count: 0

    PLAN (MON$ATTACHMENTS NATURAL)

    OUTPUT message field count: 2
    01: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name: MON$WIRE_COMPRESSED  alias: MON$WIRE_COMPRESSED
      : table: MON$ATTACHMENTS  owner: SYSDBA
    02: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name: MON$WIRE_ENCRYPTED  alias: MON$WIRE_ENCRYPTED
      : table: MON$ATTACHMENTS  owner: SYSDBA
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

