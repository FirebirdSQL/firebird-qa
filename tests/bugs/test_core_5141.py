#coding:utf-8
#
# id:           bugs.core_5141
# title:        Field definition allows several NOT NULL clauses
# decription:   
# tracker_id:   CORE-5141
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed: 
    -- * wrong behavour: WI-V3.0.0.32378 Firebird 3.0
    -- * proper result (compiler errror): WI-T4.0.0.32390 Firebird 4.0.
    recreate table t1 (a integer not null not null not null);
    recreate table t2 (a integer unique not null not null references t2(a));
    recreate table t3 (a integer unique not null references t2(a) not null);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    SQL error code = -637
    -duplicate specification of NOT NULL - not supported

    Statement failed, SQLSTATE = 42000
    SQL error code = -637
    -duplicate specification of NOT NULL - not supported

    Statement failed, SQLSTATE = 42000
    SQL error code = -637
    -duplicate specification of NOT NULL - not supported
  """

@pytest.mark.version('>=4.0')
def test_core_5141_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

