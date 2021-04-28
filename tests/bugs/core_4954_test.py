#coding:utf-8
#
# id:           bugs.core_4954
# title:        The package procedure with value by default isn't called if this parameter isn't specified.
# decription:   
# tracker_id:   CORE-4954
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
    create or alter package pkg_test
    as
    begin
      procedure p1(a int, b int = 1) returns(x int);
      function f1(a int,  b int = 1) returns int;
      procedure sp_test returns(x int);
    end
    ^

    recreate package body pkg_test
    as
    begin
      procedure p1(a int, b int) returns(x int) as
      begin
          x = a + b;
          suspend;
      end

      function f1(a int, b int) returns int as
      begin
          return a + b;
      end

      procedure sp_test returns(x int) as
      begin

        execute procedure p1( 12 ) returning_values :x; suspend;

        execute procedure p1( 12, 13 ) returning_values :x; suspend;

        select x from p1( 12 ) into x; suspend;
        select x from p1( 12, 13 ) into x; suspend;
        
        x = f1( 21 ); suspend;
        x = f1( 22, 23 ); suspend;
        
      end
    end
    ^ 
    set term ;^
    commit;


    set list on;
    select * from pkg_test.sp_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               13
    X                               25
    X                               13
    X                               25
    X                               22
    X                               45
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

