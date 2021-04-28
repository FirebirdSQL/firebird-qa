#coding:utf-8
#
# id:           functional.table.alter.02
# title:        ALTER TABLE - ADD column (test2)
# decription:   ALTER TABLE - ADD column (test2)
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.table.alter.alter_table_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TABLE test ADD text varchar(32) DEFAULT CURRENT_ROLE NOT NULL CONSTRAINT pk PRIMARY KEY;
SHOW TABLE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID                              INTEGER Nullable
TEXT                            VARCHAR(32) Not Null DEFAULT CURRENT_ROLE
CONSTRAINT PK:
  Primary key (TEXT)
"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

