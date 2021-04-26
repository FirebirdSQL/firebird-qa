#coding:utf-8
#
# id:           functional.index.alter.01
# title:        ALTER INDEX - INACTIVE
# decription:   ALTER INDEX - INACTIVE
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE INDEX
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.index.alter.alter_index_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create table test( a integer);
    create index test_idx on test(a);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter index test_idx inactive;
    commit;
    set list on;
    select
        rdb$index_name as idx_name,
        rdb$index_inactive as is_inactive
    from rdb$indices
    where rdb$index_name=upper('test_idx');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    IDX_NAME                        TEST_IDX                                                                                     
    IS_INACTIVE                     1
  """

@pytest.mark.version('>=2.0')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

