#coding:utf-8
#
# id:           bugs.core_5755
# title:        No error if the GRANT target object does not exist
# decription:   
#                  Checked on:
#                       30SS, build 3.0.4.32984: OK, 1.391s.
#                       40SS, build 4.0.0.998: OK, 1.422s.
#                  
#                  ::: NOTE :::
#                  grant execute on proc|func|package and grant usage on sequence|exception -- still does NOT produce error/warning.
#                  These statements temply disabled until some additional comments in tracker.
#                
# tracker_id:   CORE-5755
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
    recreate table table_test(x int);
    create or alter procedure sp_test as begin end;

    set term ^;
    create or alter function fn_test returns int as 
    begin 
        return cast( rand()*10000 as int );
    end
    ^

    create or alter package pkg_test as
    begin
        procedure sp_foo;
    end
    ^

    recreate package body pkg_test as
    begin
        procedure sp_foo as
            declare c int;
        begin
            c = 1;
        end
    end
    ^
    set term ;^

    recreate sequence g_test;
    recreate exception x_test 'foo!';
    commit;

    grant create table to function wrong_func;

    grant select on table_test to function wrong_func;

    
    /************ 

    TEMPLY DISABLED, SEE ISSUE IN THE TICKET, 02-JUN-2018 08:20
    ===============

    grant execute on procedure sp_test to wrong_func;

    grant execute on function fn_test to wrong_func;

    grant execute on package pkg_test to wrong_func;

    grant usage on sequence g_test to wrong_func;

    grant usage on exception x_test to wrong_func;

    **************/

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Function WRONG_FUNC does not exist
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Function WRONG_FUNC does not exist
  """

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

