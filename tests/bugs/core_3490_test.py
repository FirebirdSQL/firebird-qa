#coding:utf-8
#
# id:           bugs.core_3490
# title:        Concurrency problem when using named cursors
# decription:   
#                   ::: NB :::
#                   Result in 3.0 and 4.0 has been changed "backward" to 2.5 after CORE-5773 was fixed.
#                   Expected stdout adjusted to FB 2.5, test now contains single section
#                   (done after discuss with dimitr, letter 29-mar-2018 12:18).
#               
#                   Checked on:
#                       FB25Cs, build 2.5.8.27067: OK, 1.250s.
#                       FB25SC, build 2.5.9.27107: OK, 0.797s.
#                       FB30SS, build 3.0.4.32939: OK, 0.968s.
#                       FB40SS, build 4.0.0.943: OK, 1.297s.
#                 
# tracker_id:   CORE-3490
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table my_table (a integer, b integer,c integer);
    insert into my_table(a,b,c) values (1,1,1);
    commit;
    set transaction no wait;

    set term ^ ;
    execute block as
      declare my_cursor cursor for
        ( select b from my_table
          where a = 1 
          for update of b with lock
        );
      declare b integer;
    
    begin
      open my_cursor;
      fetch my_cursor into :b;
    
      update my_table set c = 2
      where a = 1;
      
      UPDATE MY_TABLE SET A = 0 WHERE A = 1; 

      update my_table set b = 2
      where current of my_cursor;
    end
    ^
    set term ;^
    set list on;
    select * from my_table;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               0
    B                               2
    C                               2
  """

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

