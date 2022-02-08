#coding:utf-8

"""
ID:          issue-3903
ISSUE:       3903
TITLE:       Floating-point negative zero doesn't match positive zero in the index
DESCRIPTION:
JIRA:        CORE-3547
FBTEST:      bugs.core_3547
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table t_float_no_pk (col float);
    commit;
    insert into t_float_no_pk (col) values (0e0);
    insert into t_float_no_pk (col) values (-0e0);
    commit;

    recreate table t1_double_as_pk (col double precision, constraint t1_double_pk primary key(col) using index t1_double_pk);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    where id = 0                    1
    where id = 0e0                  1
    where id = (1e0 - 1e0)          1
    where id = -0e0                 1
    where id = -(1e0 - 1e0)         1
    where 0e0 = -0e0                1
    t_float_no_pk: count(dist col)  1
    t_double_pk: col, count(*)      1
"""

expected_stderr_win = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "T1_DOUBLE_PK" on table "T1_DOUBLE_AS_PK"
    -Problematic key value is ("COL" = 0.0000000000000000)
"""

expected_stderr_non_win = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "T1_DOUBLE_PK" on table "T1_DOUBLE_AS_PK"
    -Problematic key value is ("COL" = 0.000000000000000)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_win if act.platform == 'Windows' else expected_stderr_non_win
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
