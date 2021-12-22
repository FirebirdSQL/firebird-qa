#coding:utf-8
#
# id:           bugs.core_2005
# title:        Support SQL 2008 syntax for MERGE statement with DELETE extension
# decription:   
# tracker_id:   CORE-2005
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table src(id int primary key, x int, y int, z computed by(x+y));
    recreate table tgt(id int primary key, x int, y int, z computed by(x+y));
    commit;
    
    insert into src values(1, 5, 2);
    insert into src values(3, 4, 3);
    insert into src values(5, 3, 4);
    insert into src values(6, 2, 5);
    insert into src values(7, 1, 1);
    insert into src values(8, 0, 0);
    insert into src values(9, 1, 2);
    commit;
    
    
    insert into tgt values(2, 2, 5);
    insert into tgt values(3, 3, 5);
    insert into tgt values(4, 1, 7);
    insert into tgt values(5, 6, 3);
    commit;
    
    set transaction snapshot no wait;
    
    set term ^;
    execute block as
    begin
        in autonomous transaction  do
        merge into tgt t
        using src s
        on s.id = t.id
        when not matched and s.z >= 7 then
            insert values(id, x, y)
        when matched and t.z > s.z then
            delete
        when matched then
            update set x = s.x, y = s.y
        ;
        
        merge into src t
        using tgt s
        on s.id = t.id
        when matched and t.z <= s.z then
            update set x = s.x, y = s.y
        when not matched and s.z >= 7 then
            insert values(id, x, y)
        when matched then
            delete
        ;
    end
    ^
    set term ;^
    commit;
    
    select * from src;
    select * from tgt;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID            X            Y                     Z
============ ============ ============ =====================
           1            5            2                     7
           3            3            5                     8
           5            6            3                     9
           6            2            5                     7
           7            1            1                     2
           8            0            0                     0
           9            1            2                     3
           2            2            5                     7
           4            1            7                     8


          ID            X            Y                     Z
============ ============ ============ =====================
           2            2            5                     7
           4            1            7                     8
           1            5            2                     7
           6            2            5                     7
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

