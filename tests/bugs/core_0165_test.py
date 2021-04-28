#coding:utf-8
#
# id:           bugs.core_0165
# title:        Query using VIEW with UNION causes crash
# decription:   
#                   Original test see im:
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_24.script
#                
# tracker_id:   CORE-0165
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
    recreate view v_test1 ( id, x ) as select 1, 2 from rdb$database;
    recreate view v_test2 ( id, x ) as select 1, 2 from rdb$database;
    commit;

    recreate table test1 (
      id int not null,
      x int not null);
    
    recreate table test2 (
      id int not null,
      y int not null);
    
    recreate view v_test1 ( id, x ) as
    select id, x
    from test1
    union
    select id, x
    from test1;
    
    recreate view v_test2 ( id, y ) as
    select id, y
    from test2
    union
    select id, y
    from test2;
    commit;

    insert into test1 values(1, 123);
    insert into test1 values(2, 456);
    insert into test2 values(3, 151);
    insert into test2 values(2, 456);
    insert into test2 values(1, 123);
    commit;

    set list on;
    --set plan on;
    select i.id as id_1, i.x as x, j.id as id_2, j.y as y
    from v_test1 i, v_test2 j
    where i.id = j.id
    and j.y = (select max(x.y) from v_test2 x)
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID_1                            2
    X                               456
    ID_2                            2
    Y                               456
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

