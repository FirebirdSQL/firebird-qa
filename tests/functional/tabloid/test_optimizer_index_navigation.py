#coding:utf-8
#
# id:           functional.tabloid.optimizer_index_navigation
# title:        Check that optimizer takes in account presense of index and does navigation instead of external sort.
# decription:   
#                   Verified commit: https://github.com/FirebirdSQL/firebird/actions/runs/176006556
#                   Source message to dimitr: 20.07.2020 20:00.
#               
#                   Checked on 3.0.7.33340 and 4.0.0.2114 (intermediate build with timestamp 20.07.2020 17:45)
#                 
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(x int);
    create index t_x_asc on t(x);
    create descending index t_x_dec on t(x);
    insert into t select rand()*1000 from rdb$types,rdb$types;
    commit;
    set statistics index t_x_asc;
    set statistics index t_x_dec;
    commit;
    set planonly;
     
    select * from t as t1 where x>=0.5; -- NO 'plan order' must be here; bitmap is enough!

    select * from t as t2 where x>=0.5 order by x; -- here PLAN ORDER is much efficient than bitmap + PLAN SORT

    select * from t as t3 where x<=0.5; -- NO 'plan order' must be here; bitmap is enough!

    select * from t as t4 where x<=0.5 order by x desc; -- here PLAN ORDER is much efficient than bitmap + PLAN SORT
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T1 INDEX (T_X_ASC))

    PLAN (T2 ORDER T_X_ASC)

    PLAN (T3 INDEX (T_X_ASC))

    PLAN (T4 ORDER T_X_DEC)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

