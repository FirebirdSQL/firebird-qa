#coding:utf-8
#
# id:           bugs.core_1036
# title:        extend retutnning support added in ver 2 in update record of table and in updateble view
# decription:   
#                  Only basic support is checked here (i.e. only table and one-to-one projection view, WITHOUT trigger(s)).
#                
# tracker_id:   CORE-1036
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate view v_test as select 1 x from rdb$database;
    commit;

    recreate table test(id int primary key, x int default 11, y int default 12, z computed by(x+y) );
    commit;

    recreate view v_test as select id, x, y, z from test;
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    insert into test(id, x, y) values(1,100,200);
    commit;

    insert into test(id) values(2) returning x as t_inserted_x, y as t_inserted_y, z as t_inserted_z;
    update test set id=-id, x=-2*y, y=-3*x where id=1 returning x as t_updated_x, y as t_updated_y, z as t_updated_z;
    delete from test where id < 0 returning x as t_deleted_x, y as t_deleted_y, z as t_deleted_z;

    delete from test;
    insert into test(id, x, y) values(1,100,200);
    commit;

    insert into v_test(id) values(3) returning x as v_inserted_x, y as v_inserted_y, z as v_inserted_z;
    update v_test set id=-id, x=-2*y, y=-3*x where id=1 returning x as v_updated_x, y as v_updated_y, z as v_updated_z;
    delete from v_test where id < 0 returning x as v_deleted_x, y as v_deleted_y, z as v_deleted_z;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    T_INSERTED_X                    11
    T_INSERTED_Y                    12
    T_INSERTED_Z                    23
    T_UPDATED_X                     -400
    T_UPDATED_Y                     -300
    T_UPDATED_Z                     -700
    T_DELETED_X                     -400
    T_DELETED_Y                     -300
    T_DELETED_Z                     -700

    V_INSERTED_X                    11
    V_INSERTED_Y                    12
    V_INSERTED_Z                    23
    V_UPDATED_X                     -400
    V_UPDATED_Y                     -300
    V_UPDATED_Z                     -700
    V_DELETED_X                     -400
    V_DELETED_Y                     -300
    V_DELETED_Z                     -700
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

