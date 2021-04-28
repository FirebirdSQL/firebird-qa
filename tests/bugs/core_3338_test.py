#coding:utf-8
#
# id:           bugs.core_3338
# title:        Regression: Code changes disabled support for expression indexes with COALESCE, CASE and DECODE
# decription:   
# tracker_id:   CORE-3338
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(n int); commit;
    insert into t select rand()*100 from rdb$types; commit;

    create index t_n2_coalesce on t computed by ( coalesce(n*2,0) ); commit;
    create index t_n2_decode   on t computed by ( decode( mod(n, 3), 0, coalesce(n,0), 1, iif(mod(n,7)=0, 2, 3) ) ); commit;

    -- 2.5 raises:
    -- Statement failed, SQLSTATE = HY000
    -- request synchronization error
    -- (for both variants of followed CREATE INDEX statement)

    set planonly;
    
    select * from t where coalesce(n*2,0) = 0;
    select * from t where decode( mod(n, 3), 0, coalesce(n,0), 1, iif(mod(n,7)=0, 2, 3) ) = 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T INDEX (T_N2_COALESCE))
    PLAN (T INDEX (T_N2_DECODE))
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

