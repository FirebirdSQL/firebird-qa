#coding:utf-8
#
# id:           bugs.core_4529
# title:        Allow to use index when GROUP BY on field which has DESCENDING index
# decription:   
#                    4.0.0.804: OK, 1.484s. // Before this build plan was: "PLAN SORT (T NATURAL)"
#                
# tracker_id:   CORE-4529
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(x int, y int); 
    commit;

    insert into t select rand()*5, rand()*5 
    from rdb$types; 
    commit;

    create DESCENDING index t_x_desc on t(x); 
    create DESCENDING index t_c_desc on t computed by( x+y ); 
    commit;

    set planonly;

    select x,max(y) from t group by x;
    select x,min(y) from t group by x; 

    select count(x) from t group by ( x+y );

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T ORDER T_X_DESC)
    PLAN (T ORDER T_X_DESC)
    PLAN (T ORDER T_C_DESC)
  """

@pytest.mark.version('>=4.0')
def test_core_4529_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

