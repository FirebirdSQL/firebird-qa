#coding:utf-8

"""
ID:          issue-1819
ISSUE:       1819
TITLE:       Global temporary table instance may pick up not all indices
DESCRIPTION:
JIRA:        CORE-1401
FBTEST:      bugs.core_1401
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create global temporary table t (f1 int, f2 int, f3 int);
create index idx1 on t (f1);
create index idx2 on t (f2);
create index idx3 on t (f3);
drop index idx2;

set plan on;
insert into t values (1, 1, 1);
select * from t where f1 = 1;
select * from t where f2 = 1;
select * from t where f3 = 1;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T INDEX (IDX1))

          F1           F2           F3
============ ============ ============
           1            1            1


PLAN (T NATURAL)

          F1           F2           F3
============ ============ ============
           1            1            1


PLAN (T INDEX (IDX3))

          F1           F2           F3
============ ============ ============
           1            1            1

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

