#coding:utf-8
#
# id:           bugs.core_3509
# title:        Alter procedure allows to add the parameter with the same name
# decription:   
# tracker_id:   CORE-3509
# min_versions: ['2.5.1']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create or alter procedure duplicate_output_args returns (a_dup int) as
    begin
      a_dup = 1;
    Suspend;
    end^
    set term ;^
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure duplicate_output_args returns( a_dup int, a_dup int) as
    begin
      a_dup = 1;
    Suspend;
    end
    ^
    set term ;^
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    CREATE OR ALTER PROCEDURE DUPLICATE_OUTPUT_ARGS failed
    -SQL error code = -901
    -duplicate specification of A_DUP - not supported
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

