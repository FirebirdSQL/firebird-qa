#coding:utf-8
#
# id:           bugs.core_5161
# title:        Unique index could be created on non-unique data
# decription:   
# tracker_id:   CORE-5161
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed on: WI-V3.0.0.32378, WI-V2.5.6.26980:
    -- one might to create unique index when number of inserted rows was >= 3276.

    recreate table t (id int, x int);
    set term ^;
    execute block as
        declare i int = 0;
    begin
        --while (i < 100000) do
        while (i < 50000) do -- minimal number for reproduce: 3276
        begin
            insert into t values ( :i, iif(:i=1, -888888888, -:i) );
            i = i + 1;
        end
    end
    ^
    set term ;^

    set list on;

    select sign(count(*)) as cnt_non_zero from t;

    set echo on;

    insert into t values(1, -999999999);
    commit;

    create unique index t_id_unique on t(id);

    set plan on;
    select id, x from t where id = 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT_NON_ZERO                    1
    insert into t values(1, -999999999);
    commit;
    create unique index t_id_unique on t(id);
    set plan on;
    select id, x from t where id = 1;
    PLAN (T NATURAL)
    ID                              1
    X                               -888888888
    ID                              1
    X                               -999999999
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "T_ID_UNIQUE"
    -Problematic key value is ("ID" = 1)
  """

@pytest.mark.version('>=2.5.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

