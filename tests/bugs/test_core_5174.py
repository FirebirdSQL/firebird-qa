#coding:utf-8
#
# id:           bugs.core_5174
# title:        Wrong sequence of savepoints may be produced by selectable procedure
# decription:   
# tracker_id:   CORE-5174
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    create or alter procedure ins_t1 as begin end;
    create or alter procedure ins_t2 as begin end;
    commit;

    recreate table t (f varchar(20));
    recreate exception Boom 'Boom';

    set term ^;
    create or alter procedure ins_t2 returns (a integer) as
    begin
      a = coalesce(rdb$get_context('USER_TRANSACTION', 'a'),0);
      rdb$set_context('USER_TRANSACTION', 'a', a+1);
      insert into t values (:a);
      if (a = 2) then
          exception Boom;
    end
    ^
    create or alter  procedure ins_t1 returns (a integer) as
    begin
      a = 100;
      while (1=1) do
       begin
        begin
          insert into t values (:a||'_point_a');
          execute procedure ins_t2 returning_values a;
          if (a > 4) then
            leave;
          suspend;
          insert into t values (:a||'_point_b');
        when any do begin insert into t values (-1); end
        end
       end
    end^
    commit^

    execute block returns (a integer) as
    begin
      for select a from ins_t1 into :a do
       begin
        insert into t values (:a||'_point_c');
        suspend;
        insert into t values (:a||'_point_d');
       end
    end^
    set term ;^

    select * from t;
    -- ...
    -- 1_point_d
    -- 1_point_b
    -- 1_point_a <<< this record was absent before 2016-03-28 in 4.0, see: https://github.com/FirebirdSQL/firebird/commit/6ae11453944c1d37789dd1c11913cd31829de341
    -- -1
    -- 1_point_a
    -- ...
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    0 
    1 
    3 
    4 

    100_point_a          
    0                    
    0_point_c            
    0_point_d            
    0_point_b            
    0_point_a            
    1                    
    1_point_c            
    1_point_d            
    1_point_b            
    1_point_a            
    -1                   
    1_point_a            
    3                    
    3_point_c            
    3_point_d            
    3_point_b            
    3_point_a            
    4                    
    4_point_c            
    4_point_d            
    4_point_b            
    4_point_a            
    5                    
  """

@pytest.mark.version('>=4.0')
def test_core_5174_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

