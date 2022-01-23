#coding:utf-8

"""
ID:          issue-4848
ISSUE:       4848
TITLE:       DB_KEY based join of two tables may be ineffective
DESCRIPTION:
  Order of expressions in the join condition could negatively affect the generated plan
  and thus performance
JIRA:        CORE-4530
"""

import pytest
from firebird.qa import *

init_script = """
  recreate table t (id int, constraint t_pk primary key(id) using index t_pk_idx);
  commit;
"""

db = db_factory(init=init_script)

test_script = """
  set planonly;

  -- This query had bad generated plan before fix core-4530:
  -- PLAN JOIN (X A ORDER RDB$PRIMARY4, Z NATURAL)
  select count(*)
  from (select id, rdb$db_key k from t a order by id) x
  left join t z on x.k = z.rdb$db_key; -------------------- left side: `x.k`, right side: `z.rdb$db_key`

  select count(*)
  from (select id, rdb$db_key k from t a order by id) x
  left join t z on z.rdb$db_key = x.k; -------------------- left side: `z.rdb$db_key`, right side: `x.k`
"""

act = isql_act('db', test_script)

expected_stdout = """
  PLAN JOIN (X A ORDER T_PK_IDX, Z INDEX ())
  PLAN JOIN (X A ORDER T_PK_IDX, Z INDEX ())
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

