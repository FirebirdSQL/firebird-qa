#coding:utf-8

"""
ID:          issue-1420
ISSUE:       1420
TITLE:       Local buffer overrun in DYN_error() that takes down the server
DESCRIPTION:
  We have a local buffer overrun in DYN_error(), while copying tdbb_status_vector to
  local_status. It seems to be the first time (DYN errors + stack trace facility) when 20
  status words are not enough to store the complete error info.
JIRA:        CORE-1010
FBTEST:      bugs.core_1010
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Removed old code: all attempts to create triggers on SYSTEM tables now are prohibited, even for SYSDBA.
    create exception ex_test '!!!';
    commit;

    set term ^ ;
    create or alter trigger rdb$procedures_biu for rdb$procedures
    active after update or delete position 0
    as
    begin
        exception ex_test;
    end
    ^
    commit^

    create or alter procedure proctest returns (result integer) as
    begin
        result = 0;
        suspend;
    end^
    set term ; ^
    commit;
"""

act = isql_act('db', test_script, substitutions=[('line:.*', ''), ('col:.*', '')])

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER RDB$PROCEDURES_BIU failed
    -no permission for ALTER access to TABLE RDB$PROCEDURES
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

