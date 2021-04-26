#coding:utf-8
#
# id:           bugs.core_3343
# title:        RETURNING clause is not supported in positioned (WHERE CURRENT OF) UPDATE and DELETE statements
# decription:   
# tracker_id:   CORE-3343
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('VB_.*', '')]

init_script_1 = """
    recreate table test_a(id integer, cnt integer);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block
    as
      declare variable cnt integer;
    begin
       for select cnt from test_a
          where id=1
          into :cnt as cursor c
          do begin
             update test_a
                set cnt=cnt+1
              where current of c
              returning cnt into :cnt;
          end
    end 
    ^
    set term ;^
    commit;

    -- from core-3709 (refactored: check results when operating with blob):
    recreate table test(
       i int
      ,b blob sub_type 1
    );
    insert into test(i,b) values(1, 'qwe');
    commit;

    set blob all;
    set list on;

    set term ^;
    execute block returns(vb_old blob, vb_new blob) as
       declare c cursor for (  select b from test where i = 1 );
       declare v_s varchar(20);
    begin
       open c;
       while (1=1) do
       begin
         fetch c into :v_s;
         if (row_count = 0) then leave;
         update test set b = reverse(b) 
         where current of c 
         returning upper(old.b), upper(new.b) into vb_old, vb_new
         ;
         suspend;
       end
       close c;
    end
    ^
    set term ;^
    commit;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    QWE
    EWQ
  """

@pytest.mark.version('>=3.0')
def test_core_3343_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

