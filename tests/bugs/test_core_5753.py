#coding:utf-8
#
# id:           bugs.core_5753
# title:        Parser allows to use GRANT OPTION for FUNCTION and PACKAGE
# decription:   
#                   Confirmed bug on: 4.0.0.890; 3.0.4.32912
#                   Works fine on:
#                       3.0.4.32917: OK, 0.937s.
#                       4.0.0.907: OK, 1.187s.
#                
# tracker_id:   CORE-5753
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    
    set term ^;
    create or alter procedure sp_test as
    begin
    end
    ^
    create or alter function sa_func(a int) returns bigint as
    begin
      return a * a;
    end
    ^
    recreate package pg_test as
    begin
        function pg_func(a int) returns bigint;
    end
    ^
    create package body pg_test as
    begin
        function pg_func(a int) returns bigint as
        begin
            return a * a;
        end
    end
    ^
    set term ;^
    commit;

    -- following two statements have to raise error (but did not before fix):
    grant execute on procedure sp_test to function sa_func with grant option;
    grant execute on procedure sp_test to package pg_test with grant option;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Dynamic SQL Error
    -Using GRANT OPTION on functions not allowed

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Dynamic SQL Error
    -Using GRANT OPTION on packages not allowed
  """

@pytest.mark.version('>=3.0.4')
def test_core_5753_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

