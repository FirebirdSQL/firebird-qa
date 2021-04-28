#coding:utf-8
#
# id:           bugs.core_4530
# title:        DB_KEY based join of two tables may be ineffective
# decription:   Order of expressions in the join condition could negatively affect the generated plan and thus performance
# tracker_id:   CORE-4530
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
  recreate table t (id int, constraint t_pk primary key(id) using index t_pk_idx);
  commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  PLAN JOIN (X A ORDER T_PK_IDX, Z INDEX ())
  PLAN JOIN (X A ORDER T_PK_IDX, Z INDEX ())
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

