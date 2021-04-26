#coding:utf-8
#
# id:           functional.index.alter.02
# title:        ALTER INDEX
# decription:   ALTER INDEX
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE INDEX
#               ALTER INDEX
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.index.alter.alter_index_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create table test_active_state_toggle( a integer);
    commit;
    create index test_active_state_toggle_idx on test_active_state_toggle(a);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter index test_active_state_toggle_idx inactive;
    alter index test_active_state_toggle_idx active;
    commit;
    set list on;
    select rdb$index_name, rdb$index_inactive
    from rdb$indices
    where rdb$index_name=upper('test_active_state_toggle_idx');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$INDEX_NAME                  TEST_ACTIVE_STATE_TOGGLE_IDX
    RDB$INDEX_INACTIVE              0
  """

@pytest.mark.version('>=2.0')
def test_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

