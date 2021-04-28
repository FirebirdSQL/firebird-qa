#coding:utf-8
#
# id:           bugs.core_3137
# title:        Partial rollback is possible for a selectable procedure modifying data
# decription:   
# tracker_id:   CORE-3137
# min_versions: ['2.1.4']
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter procedure sp_01 returns (ret int) as begin end;
    commit;
    recreate table tab (col int);
    commit;
    insert into tab (col) values (1);
    commit;
    
    set term ^;
    create or alter procedure sp_01 returns (ret int) as
    begin
        update tab set col = 2;
        begin
            update tab set col = 3;
            ret = 1;
            suspend;
        end
        when any do
        begin
            ret = 0;
            suspend;
        end
    end
    ^ set term ;^
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select col from tab; -- returns 1
    commit;

    select ret from sp_01;
    rollback;

    select col from tab; -- returns 2!!!
    commit; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COL                             1
    RET                             1
    COL                             1
  """

@pytest.mark.version('>=2.1.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

