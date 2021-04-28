#coding:utf-8
#
# id:           bugs.core_4817
# title:        ISQL doesn`t show number of affected rows for "MERGE ... WHEN MATCHING" in case when this number surely > 0
# decription:   
# tracker_id:   CORE-4817
# min_versions: ['2.5.6']
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
    recreate table src(id int, x int);
    commit;
    
    insert into src
    with recursive r as(select 0 i from rdb$database union all select r.i+1 from r where r.i<9)
    select r.i, r.i * 2 from r;
    commit;
    
    recreate table tgt(id int primary key, x int);
    commit;
    
    set count on;
    merge into tgt t
    using (select * from src where id > 1) s on s.id = t.id
    when not matched then insert values(s.id, s.x); 
    commit;
    
    merge into tgt t
    using src s on s.id = t.id
    when matched and s.id in (7,8,9) then update set t.x = -2 * s.x;
    rollback;
    
    merge into tgt t
    using src s on s.id = t.id
    when matched and s.id in (0,1,2) then update set t.x = -2 * s.x
    when not matched and s.id = 0 then insert values(s.id, 1111)
    when matched and s.id in (3,4,5,6) then update set t.x = - 3 * s.x
    when not matched and s.id = 1 then insert values(s.id, 2222)
    when matched then delete
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
   Records affected: 8
   Records affected: 3
   Records affected: 10
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

