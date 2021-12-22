#coding:utf-8
#
# id:           functional.index.alter.03
# title:        ALTER INDEX - INACTIVE UNIQUE INDEX
# decription:   ALTER INDEX - INACTIVE UNIQUE INDEX
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE INDEX
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.index.alter.alter_index_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create table test( a integer);
    create unique index test_idx_unq on test(a);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    alter index test_idx_unq inactive;
    commit;
    set list on;
    select
        rdb$index_name as idx_name
        ,rdb$index_inactive as is_inactive
        ,r.rdb$unique_flag as is_unique
    from rdb$indices r
    where rdb$index_name=upper('test_idx_unq');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    IDX_NAME                        TEST_IDX_UNQ                                                                                 
    IS_INACTIVE                     1
    IS_UNIQUE                       1
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

