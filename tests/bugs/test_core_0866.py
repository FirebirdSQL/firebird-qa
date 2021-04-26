#coding:utf-8
#
# id:           bugs.core_866
# title:        Removing a NOT NULL constraint is not visible until reconnect
# decription:   
# tracker_id:   CORE-866
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_866

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test (
        id integer not null,
        col varchar(20) not null
    );
    insert into test (id, col) values (1, 'data');
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    update rdb$relation_fields
      set rdb$null_flag = null
      where (rdb$field_name = upper('col')) and (rdb$relation_name = upper('test'));
    commit;

    update test set col = null where id = 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$RELATION_FIELDS
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."COL", value "*** null ***"
   """

@pytest.mark.version('>=3.0')
def test_core_866_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

