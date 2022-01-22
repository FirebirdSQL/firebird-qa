#coding:utf-8

"""
ID:          issue-3704
ISSUE:       3704
TITLE:       Regression: Code changes disabled support for expression indexes with COALESCE, CASE and DECODE
DESCRIPTION:
JIRA:        CORE-3338
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t(n int); commit;
    insert into t select rand()*100 from rdb$types; commit;

    create index t_n2_coalesce on t computed by ( coalesce(n*2,0) ); commit;
    create index t_n2_decode   on t computed by ( decode( mod(n, 3), 0, coalesce(n,0), 1, iif(mod(n,7)=0, 2, 3) ) ); commit;

    set planonly;

    select * from t where coalesce(n*2,0) = 0;
    select * from t where decode( mod(n, 3), 0, coalesce(n,0), 1, iif(mod(n,7)=0, 2, 3) ) = 1;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T INDEX (T_N2_COALESCE))
    PLAN (T INDEX (T_N2_DECODE))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

