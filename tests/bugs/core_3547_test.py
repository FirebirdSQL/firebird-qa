#coding:utf-8
#
# id:           bugs.core_3547
# title:        Floating-point negative zero doesn't match positive zero in the index
# decription:
# tracker_id:   CORE-3547
# min_versions: ['2.5.1']
# versions:     2.5.1, 2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t_float_no_pk (col float);
    commit;
    insert into t_float_no_pk (col) values (0e0);
    insert into t_float_no_pk (col) values (-0e0);
    commit;

    recreate table t1_double_as_pk (col double precision, constraint t1_double_pk primary key(col) using index t1_double_pk);
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select count(*) "where id = 0"            from rdb$relations where rdb$relation_id = 0;
    select count(*) "where id = 0e0"          from rdb$relations where rdb$relation_id = 0e0;
    select count(*) "where id = (1e0 - 1e0)"  from rdb$relations where rdb$relation_id = (1e0 - 1e0);
    select count(*) "where id = -0e0"         from rdb$relations where rdb$relation_id = -0e0;
    select count(*) "where id = -(1e0 - 1e0)" from rdb$relations where rdb$relation_id = -(1e0 - 1e0);
    select count(*) "where 0e0 = -0e0"        from rdb$database where 0e0 = -0e0;

    insert into t1_double_as_pk (col) values (0e0);
    commit;
    insert into t1_double_as_pk (col) values (-0e0);
    commit;
    select count(distinct col) "t_float_no_pk: count(dist col)" from t_float_no_pk;
    select count(*) "t_double_pk: col, count(*)" from t1_double_as_pk group by col;
    -- :: NB ::: Problematic key representaion for 0e0 differ in Windows vs Linux!
    -- NIX: -Problematic key value is ("COL" = 0.000000000000000)
    -- WIN: -Problematic key value is ("COL" = 0.0000000000000000)
    --                                                          ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    where id = 0                    1
    where id = 0e0                  1
    where id = (1e0 - 1e0)          1
    where id = -0e0                 1
    where id = -(1e0 - 1e0)         1
    where 0e0 = -0e0                1
    t_float_no_pk: count(dist col)  1
    t_double_pk: col, count(*)      1
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "T1_DOUBLE_PK" on table "T1_DOUBLE_AS_PK"
    -Problematic key value is ("COL" = 0.0000000000000000)
"""

@pytest.mark.version('>=2.5.1')
@pytest.mark.platform('Windows')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 2.5.1
# resources: None

substitutions_2 = []

init_script_2 = """
    recreate table t_float_no_pk (col float);
    commit;
    insert into t_float_no_pk (col) values (0e0);
    insert into t_float_no_pk (col) values (-0e0);
    commit;

    recreate table t1_double_as_pk (col double precision, constraint t1_double_pk primary key(col) using index t1_double_pk);
    commit;
"""

db_2 = db_factory(page_size=4096, sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    select count(*) "where id = 0"            from rdb$relations where rdb$relation_id = 0;
    select count(*) "where id = 0e0"          from rdb$relations where rdb$relation_id = 0e0;
    select count(*) "where id = (1e0 - 1e0)"  from rdb$relations where rdb$relation_id = (1e0 - 1e0);
    select count(*) "where id = -0e0"         from rdb$relations where rdb$relation_id = -0e0;
    select count(*) "where id = -(1e0 - 1e0)" from rdb$relations where rdb$relation_id = -(1e0 - 1e0);
    select count(*) "where 0e0 = -0e0"        from rdb$database where 0e0 = -0e0;

    insert into t1_double_as_pk (col) values (0e0);
    commit;
    insert into t1_double_as_pk (col) values (-0e0);
    commit;
    select count(distinct col) "t_float_no_pk: count(dist col)" from t_float_no_pk;
    select count(*) "t_double_pk: col, count(*)" from t1_double_as_pk group by col;
    -- :: NB ::: Problematic key representaion for 0e0 differ in Windows vs Linux!
    -- NIX: -Problematic key value is ("COL" = 0.000000000000000)
    -- WIN: -Problematic key value is ("COL" = 0.0000000000000000)
    --                                                          ^
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    where id = 0                    1
    where id = 0e0                  1
    where id = (1e0 - 1e0)          1
    where id = -0e0                 1
    where id = -(1e0 - 1e0)         1
    where 0e0 = -0e0                1
    t_float_no_pk: count(dist col)  1
    t_double_pk: col, count(*)      1
"""
expected_stderr_2 = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "T1_DOUBLE_PK" on table "T1_DOUBLE_AS_PK"
    -Problematic key value is ("COL" = 0.000000000000000)
"""

@pytest.mark.version('>=2.5.1')
@pytest.mark.platform('Linux', 'Darwin', 'Solaris', 'FreeBSD', 'HP-UX')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr
    assert act_2.clean_stdout == act_2.clean_expected_stdout

