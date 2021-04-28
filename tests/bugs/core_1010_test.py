#coding:utf-8
#
# id:           bugs.core_1010
# title:        Local buffer overrun in DYN_error() that takes down the server
# decription:   We have a local buffer overrun in DYN_error(), while copying tdbb_status_vector to local_status. It seems to be the first time (DYN errors + stack trace facility) when 20 status words are not enough to store the complete error info.
# tracker_id:   CORE-1010
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1010-21

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('line:.*', ''), ('col:.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE OR ALTER TRIGGER RDB$PROCEDURES_BIU failed
    -no permission for ALTER access to TABLE RDB$PROCEDURES
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

