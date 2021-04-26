#coding:utf-8
#
# id:           bugs.core_4665
# title:        Wrong result when use "where <field_C> STARTING WITH <:value> ORDER BY <field_N>" and field_C is leading part of compound index key: { field_C, field_N }
# decription:   
# tracker_id:   CORE-4665
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test (id int, unit varchar(10), y int, z int);
    commit;
    delete from test;
    
    insert into test( id, unit, y, z) values (1, 'foo', 9999, 23636);
    insert into test( id, unit, y, z) values (2, 'foo', 8888, 22520);
    insert into test( id, unit, y, z) values (3, 'foo', 5555, 21822);
    insert into test( id, unit, y, z) values (4, 'foo', 3333, 17682);
    
    insert into test( id, unit, y, z) values (5, 'fooo', 1111, 22);
    insert into test( id, unit, y, z) values (6, 'fooo', 111, 222);
    insert into test( id, unit, y, z) values (7, 'fooo', 11, 2222);
    insert into test( id, unit, y, z) values (8, 'fooo', 1, 22222);
    commit;
    
    create index test_unit_y_asc on test( unit, y );
    commit; 

    set plan on;
    
    select id, t.unit, t.y, t.z
    from test t
    where t.unit||'' starting with 'foo'
    order by t.y||'';
    
    select id, t.unit, t.y, t.z
    from test t
    where t.unit starting with 'foo'
    order by t.y; 
    set plan off;
    
    commit;
    drop index test_unit_y_asc;
    commit;
    
    create descending index test_unit_y_desc on test( unit, y);
    commit; 
    
    set plan on;
    select id, t.unit, t.y, t.z
    from test t
    where t.unit starting with 'foo'
    order by t.y; 
    set plan off;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (T NATURAL)
    
              ID UNIT                  Y            Z 
    ============ ========== ============ ============ 
               8 fooo                  1        22222 
               7 fooo                 11         2222 
               6 fooo                111          222 
               5 fooo               1111           22 
               4 foo                3333        17682 
               3 foo                5555        21822 
               2 foo                8888        22520 
               1 foo                9999        23636 
    
    
    PLAN SORT (T INDEX (TEST_UNIT_Y_ASC))
    
              ID UNIT                  Y            Z 
    ============ ========== ============ ============ 
               8 fooo                  1        22222 
               7 fooo                 11         2222 
               6 fooo                111          222 
               5 fooo               1111           22 
               4 foo                3333        17682 
               3 foo                5555        21822 
               2 foo                8888        22520 
               1 foo                9999        23636 
    
    
    PLAN SORT (T INDEX (TEST_UNIT_Y_DESC))
    
              ID UNIT                  Y            Z 
    ============ ========== ============ ============ 
               8 fooo                  1        22222 
               7 fooo                 11         2222 
               6 fooo                111          222 
               5 fooo               1111           22 
               4 foo                3333        17682 
               3 foo                5555        21822 
               2 foo                8888        22520 
               1 foo                9999        23636 
  """

@pytest.mark.version('>=3.0')
def test_core_4665_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

