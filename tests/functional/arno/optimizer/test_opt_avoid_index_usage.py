#coding:utf-8
#
# id:           functional.arno.optimizer.opt_avoid_index_usage
# title:        AVOID index usage in WHERE <indexed_varchar_field> = <integer_value>
# decription:   
#                  Samples here are from CORE-3051.
#                  Confirmed usage 'PLAN INDEX ...' in FB 2.0.0.12724
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         functional.arno.optimizer.opt_avoid_index_usage

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t(x varchar(10), y varchar(10));
    create index t_x_asc on t(x);
    create descending index t_y_desc on t(y);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    --set echo on;
    select * from t where x = 0; 
    select * from t where y = 0; 
    select * from t where x > 0; 
    select * from t where y < 0; 
    select * from t where x between 0 and 1;
    select * from t where y between 0 and 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
  """

@pytest.mark.version('>=2.5.0')
def test_opt_avoid_index_usage_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

