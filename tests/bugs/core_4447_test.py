#coding:utf-8
#
# id:           bugs.core_4447
# title:        Positioned UPDATE statement prohibits index usage for the subsequent cursor field references
# decription:   
# tracker_id:   CORE-4447
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
  recreate table ts(id int, x int, y int, z int, constraint ts_pk_id primary key (id) );
  recreate table tt(x int, y int, z int, constraint tt_pk_xy primary key (x,y) );
  commit;

  insert into ts
  select row_number()over(), rand()*10, rand()*10, rand()*10
  from rdb$types;
  commit;

  insert into tt select distinct x,y,0 from ts;
  commit; 
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
  set planonly;
  set term ^;
  execute block as
  begin
    for select id,x,y,z from ts as cursor c
    do begin
       update ts set id = id where current of c; -- <<<<<<<<<<<<<<< ::: NB ::: we lock record in source using "current of" clause
       update tt t set t.z = t.z + c.z where t.x=c.x and t.y = c.y;
    end
  end
  ^ set term ;^
  set planonly;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  PLAN (T INDEX (TT_PK_XY))
  PLAN (C TS NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

