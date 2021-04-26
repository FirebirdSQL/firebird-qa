#coding:utf-8
#
# id:           bugs.core_1624
# title:        MERGE not correctly worked with parameters in MATCHING clause
# decription:   
# tracker_id:   CORE-1624
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table src(id int, x int);
    recreate table tgt(id int, x int);
    commit;
    insert into src values(1, 100);
    insert into src values(2, 200);
    insert into src values(3, 300);
    insert into src values(4, 400);
    commit;
    insert into tgt values(2, 10);
    insert into tgt values(3, 20);
    commit;  
    set term ^;
    execute block as
      declare v_stt varchar(255);
    begin
      v_stt =
          'merge into tgt t using src s on s.id = t.id '
          || 'when matched then update set t.x = s.x + ?'
          || 'when NOT matched then insert values(s.id, s.id + ?)';
    
      execute statement (v_stt) ( 1000, 20000 );
    end
    ^
    set term ;^
    select * from tgt;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
              ID            X
    ============ ============
               2         1200
               3         1300
               1        20001
               4        20004
  """

@pytest.mark.version('>=2.5')
def test_core_1624_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

