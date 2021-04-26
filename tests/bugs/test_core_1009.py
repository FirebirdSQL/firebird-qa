#coding:utf-8
#
# id:           bugs.core_1009
# title:        Restoring RDB$BASE_FIELD for expression
# decription:   RDB$BASE_FIELD for expression have to be NULL
# tracker_id:   CORE-1009
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1009

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core1009.fbk', init=init_script_1)

test_script_1 = """
  set list on;
  select rdb$field_name, rdb$base_field from rdb$relation_fields where rdb$relation_name = 'TEST_VIEW';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  ID
    RDB$BASE_FIELD                  ID
    RDB$FIELD_NAME                  EXPR
    RDB$BASE_FIELD                  <null>
  """

@pytest.mark.version('>=2.1')
def test_core_1009_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

