#coding:utf-8

"""
ID:          issue-3188
ISSUE:       3188
TITLE:       Incomplete plan output (lack of view names) when selecting from views containing procedures inside
DESCRIPTION:
JIRA:        CORE-2798
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table t1 (col int);
    commit;

    set term ^;
    create procedure p1 returns (res int) as begin suspend; end^
    set term ;^
    commit;

    create view v as select 1 as num from t1, t1 as t2, p1, p1 as p2;
    commit;
    set plan on;
    select * from v;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (V P1 NATURAL, V P2 NATURAL, V T1 NATURAL, V T2 NATURAL)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

