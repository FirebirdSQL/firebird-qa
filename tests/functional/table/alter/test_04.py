#coding:utf-8
#
# id:           functional.table.alter.04
# title:        ALTER TABLE - ADD CONSTRAINT - UNIQUE
# decription:   ALTER TABLE - ADD CONSTRAINT - UNIQUE
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.table.alter.alter_table_04

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TABLE test ADD CONSTRAINT unq UNIQUE(id);
SHOW TABLE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID                              INTEGER Not Null
CONSTRAINT UNQ:
  Unique key (ID)
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

