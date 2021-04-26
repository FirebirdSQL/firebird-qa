#coding:utf-8
#
# id:           bugs.core_2200
# title:        Extremely slow executing a cross join of 3 tables in Firebird 2.X
# decription:   
# tracker_id:   CORE-2200
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
    -- Confirmed: wrong plan on 2.0.0.12724 and 2.1.0.17798: 'T2' was choosen as drive source,
    -- absence of rows in T3 was ignored, used: PLAN JOIN (T2 NATURAL, T1 NATURAL, T3 NATURAL)

    recreate table t0(id int);
    recreate table t1(id int);
    recreate table t2(id int);
    recreate table t3(id int);
    commit;

    insert into t0 select 1 from rdb$types; -- ,rdb$types;
    commit;


    insert into t1 select * from t0;
    insert into t2 select * from t0;
    --------- ::: NB ::: we do NOT add any row to the table `t3`, it remains empty -----------
    commit;

    set list on;
    select case when count(*) > 100 then 'OK' else 'WRONG' end as t1_has_enough_rows from t1;
    select case when count(*) > 100 then 'OK' else 'WRONG' end as t2_has_enough_rows from t2;

    set plan on;
    set echo on;

    select count(*) from t1, t2, t3;

    select count(*) from t2, t3, t1;

    select count(*) from t3, t2, t1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    T1_HAS_ENOUGH_ROWS              OK   
    T2_HAS_ENOUGH_ROWS              OK   

    select count(*) from t1, t2, t3;
    PLAN JOIN (T3 NATURAL, T1 NATURAL, T2 NATURAL)
    COUNT                           0

    select count(*) from t2, t3, t1;
    PLAN JOIN (T3 NATURAL, T2 NATURAL, T1 NATURAL)
    COUNT                           0

    select count(*) from t3, t2, t1;
    PLAN JOIN (T3 NATURAL, T2 NATURAL, T1 NATURAL)
    COUNT                           0
  """

@pytest.mark.version('>=2.5')
def test_core_2200_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

