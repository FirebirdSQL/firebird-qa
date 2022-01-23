#coding:utf-8

"""
ID:          issue-4847
ISSUE:       4847
TITLE:       Allow to use index when GROUP BY on field which has DESCENDING index
DESCRIPTION:
JIRA:        CORE-4529
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T ORDER T_X_DESC)
    PLAN (T ORDER T_X_DESC)
    PLAN (T ORDER T_C_DESC)
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

