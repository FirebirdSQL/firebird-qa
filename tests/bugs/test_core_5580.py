#coding:utf-8
#
# id:           bugs.core_5580
# title:        Signature of packaged functions is not checked for mismatch with [NOT] DETERMINISTIC attribute
# decription:   
#                  Confirmed bug on builds: 3.0.3.32756, 4.0.0.690.
#                  Works fine on:
#                    3.0.3.32757: OK, 0.812s.
#                    4.0.0.693: OK, 1.047s.
#                
# tracker_id:   CORE-5580
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
    recreate package pk1 as
    begin
        function f1() returns int deterministic;
        function f2() returns int not deterministic;
    end
    ^
    recreate package body pk1 as
    begin
        function f1() returns int not deterministic as
        begin
            return 123;
        end
        
        function f2() returns int not deterministic as
        begin
            return 123 * rand();
        end
        
    end
    ^
    set term ;^
    commit;

    set list on;

    select pk1.f1() as f1_result from rdb$database;
    select pk1.f2() as f2_result  from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -RECREATE PACKAGE BODY PK1 failed
    -Function F1 has a signature mismatch on package body PK1
    Statement failed, SQLSTATE = 2F000
    Cannot execute function F1 of the unimplemented package PK1
    Statement failed, SQLSTATE = 2F000
    Cannot execute function F2 of the unimplemented package PK1
  """

@pytest.mark.version('>=3.0')
def test_core_5580_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

