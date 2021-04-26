#coding:utf-8
#
# id:           bugs.core_3394
# title:        Failed attempt to violate unique constraint could leave unneeded "lock conflict" error in status-vector
# decription:   
# tracker_id:   CORE-3394
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(id int, constraint t_pk primary key(id) using index t_id);
    commit;
    SET TRANSACTION READ COMMITTED RECORD_VERSION NO WAIT;
    set term ^;
    execute block as
    begin
      insert into t values(1);
      in autonomous transaction do
      insert into t values(1);
    end
    ^
    set term ;^
    rollback;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "T_PK" on table "T"
    -Problematic key value is ("ID" = 1)
    -At block line: 5, col: 7
  """

@pytest.mark.version('>=2.5.1')
def test_core_3394_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

