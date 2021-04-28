#coding:utf-8
#
# id:           bugs.core_2374
# title:        ALTER TRIGGER / PROCEDURE wrong error message
# decription:   
# tracker_id:   CORE-2374
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    alter procedure test1 as
    begin
      if (a = b) then
       b = 1;
    end
    ^
    alter trigger trg1 as
    begin
      if (a = b) then
       b = 1;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER PROCEDURE TEST1 failed
    -Procedure TEST1 not found
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TRIGGER TRG1 failed
    -Trigger TRG1 not found
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

