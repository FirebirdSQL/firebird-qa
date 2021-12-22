#coding:utf-8
#
# id:           bugs.core_2971
# title:        Invalid UPDATE OR INSERT usage may lead to successive "request depth exceeded. (Recursive definition?)" error
# decription:   
# tracker_id:   CORE-2971
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- This syntax works fine since 2.0.x:
    recreate view v(x, y) as select 1 x, 2 y from rdb$database;
    commit;
    set term ^;
    execute block as
    begin
      execute statement 'drop sequence g';
      when any do begin end
    end
    ^
    set term ;^
    commit;
    
    create sequence g;
    recreate table t1 (n1 integer);
    recreate table t2 (n2 integer);
    
    recreate view v(x, y) as select t1.n1 as x, t2.n2 as y from t1, t2;
    commit;
    
    set term ^;
    execute block as
      declare n int = 1000;
    begin
        while (n>0) do
        begin
            n = n - 1;
            execute statement ('update or insert into v values ( '|| gen_id(g,1) ||', gen_id(g,1))');
            -- ^
            -- For this statement trace 2.5 and 3.0 shows:
            -- ERROR AT JStatement::prepare
            -- ...
            -- 335544569 : Dynamic SQL Error
            -- 336003101 : UPDATE OR INSERT without MATCHING could not be used with views based on more than one table
            -- We have to suppress ONLY exception with gdscode = 335544569 and raise if its gdscode has any other value.
        when any do 
            begin
              if  ( gdscode not in (335544569) ) then exception;
            end
        end
    
    end
    ^
    set term ;^
    rollback;
    set list on;
    select gen_id(g, 0) curr_gen from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CURR_GEN                        1000
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

