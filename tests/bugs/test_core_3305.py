#coding:utf-8
#
# id:           bugs.core_3305
# title:        "BLOB not found" error after creation/altering of the invalid trigger
# decription:   
# tracker_id:   CORE-3305
# min_versions: ['2.5.3']
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
    recreate table t(v int);
    commit;
    set term ^;
    create or alter trigger t_ai for t active after insert position 0 as
    begin
        new.v = 1;
    end
    ^
    set term ;^
    commit;
    insert into t(v) values(123);
    rollback;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column T.V
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column T.V
  """

@pytest.mark.version('>=4.0')
def test_core_3305_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

