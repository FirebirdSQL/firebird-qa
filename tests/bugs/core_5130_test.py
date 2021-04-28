#coding:utf-8
#
# id:           bugs.core_5130
# title:        Compiler issues message about "invalid request BLR" when attempt to compile wrong DDL of view with both subquery and "WITH CHECK OPTION" in its DDL
# decription:   
# tracker_id:   CORE-5130
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed proper result on:  WI-V3.0.0.32380
    create or alter view v1 as select 1 id from rdb$database;
    recreate table t1(id int, x int, y int);
    commit;

    alter view v1 as
    select * from t1 a
    where
        not exists(select * from t1 r where r.x > a.x)
    with check option
    ; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER VIEW V1 failed
    -Dynamic SQL Error
    -SQL error code = -607
    -No subqueries permitted for VIEW WITH CHECK OPTION
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

