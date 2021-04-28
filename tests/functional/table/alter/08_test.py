#coding:utf-8
#
# id:           functional.table.alter.08
# title:        ALTER TABLE - DROP
# decription:   ALTER TABLE - DROP
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               SHOW TABLE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.table.alter.alter_table_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL,
                   text VARCHAR(32));
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TABLE test DROP text;
SHOW TABLE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID                              INTEGER Not Null
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

