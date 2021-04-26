#coding:utf-8
#
# id:           functional.table.create.02
# title:        CREATE TABLE - column properties
# decription:   CREATE TABLE - column properties
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.table.create.create_table_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE fk(id INT NOT NULL PRIMARY KEY);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE test(
 c1 SMALLINT NOT NULL,
 c2 INTEGER DEFAULT 0,
 c3 FLOAT NOT NULL UNIQUE,
 c4 DOUBLE PRECISION NOT NULL PRIMARY KEY,
 c5 INT REFERENCES fk(id),
 c6 INT CHECK (c6>c5),
 c7 COMPUTED (c1+c2),
 c8 CHAR(31) DEFAULT USER,
 c9 VARCHAR(40) DEFAULT 'data'
);
SHOW TABLE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """C1                              SMALLINT Not Null
C2                              INTEGER Nullable DEFAULT 0
C3                              FLOAT Not Null
C4                              DOUBLE PRECISION Not Null
C5                              INTEGER Nullable
C6                              INTEGER Nullable
C7                              Computed by: (c1+c2)
C8                              CHAR(31) Nullable DEFAULT USER
C9                              VARCHAR(40) Nullable DEFAULT 'data'
CONSTRAINT INTEG_8:
  Foreign key (C5)    References FK (ID)
CONSTRAINT INTEG_7:
  Primary key (C4)
CONSTRAINT INTEG_5:
  Unique key (C3)
CONSTRAINT INTEG_9:
  CHECK (c6>c5)
"""

@pytest.mark.version('>=2.1')
def test_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

