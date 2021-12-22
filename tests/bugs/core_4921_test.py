#coding:utf-8
#
# id:           bugs.core_4921
# title:        Predicate IS [NOT] DISTINCT FROM is not pushed into unions/aggregates thus causing sub-optimal plans
# decription:   
#                  Implementation for 3.0 does NOT use 'set explain on' (decision after discuss with Dmitry, letter 02-sep-2015 15:42).
#                  Test only checks that:
#                  1) in case when NATURAL scan occured currently index T*_SINGLE_X is used;
#                  2) in case when it was only PARTIAL matching index Y*_COMPOUND_X is in use.
#                  Checked on: 3.0.0.32020 and 2.5.5.26926 - all versions before those produced suboptimal of inefficient plan.
#                
# tracker_id:   CORE-4921
# min_versions: ['2.5.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter view v_test as select 1 id from rdb$database;
    commit;
    
    recreate table t1(x int, y int);
    create index t1_single_x on t1(x);
    create index t1_compound_x_y on t1(x, y);
    
    recreate table t2(x int, y int);
    create index t2_single_x on t2(x);
    create index t2_compound_x_y on t2(x, y);
    
    recreate table t3(x int, y int);
    create index t3_single_x on t3(x);
    create index t3_compound_x_y on t3(x, y);
    commit;
    
    create or alter view v_test as
    select * from t1
    union all
    select * from t2
    union all
    select * from t3;
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select * from v_test where x is not distinct from 1;
    select * from v_test where x = 1 and y is not distinct from 1;
    set planonly;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (V_TEST T1 INDEX (T1_SINGLE_X), V_TEST T2 INDEX (T2_SINGLE_X), V_TEST T3 INDEX (T3_SINGLE_X))
    PLAN (V_TEST T1 INDEX (T1_COMPOUND_X_Y), V_TEST T2 INDEX (T2_COMPOUND_X_Y), V_TEST T3 INDEX (T3_COMPOUND_X_Y))  
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

