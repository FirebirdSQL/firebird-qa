#coding:utf-8
#
# id:           functional.table.create.04
# title:        CREATE TABLE - constraints
# decription:   CREATE TABLE - constraints
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.table.create.create_table_04

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
 c2 SMALLINT NOT NULL,
 c3 SMALLINT NOT NULL,
 PRIMARY KEY(c1),
 UNIQUE(c2),
 FOREIGN KEY (c2) REFERENCES fk(id) ON DELETE CASCADE,
 CHECK (c2>c1),
 CONSTRAINT test UNIQUE(c3),
 CONSTRAINT test2 FOREIGN KEY (c3) REFERENCES fk(id) ON DELETE SET NULL,
 CONSTRAINT test3 CHECK (NOT c3>c1)
);
SHOW TABLE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """C1                              SMALLINT Not Null
C2                              SMALLINT Not Null
C3                              SMALLINT Not Null
CONSTRAINT INTEG_8:
  Foreign key (C2)    References FK (ID) On Delete Cascade
CONSTRAINT TEST2:
  Foreign key (C3)    References FK (ID) On Delete Set Null
CONSTRAINT INTEG_6:
  Primary key (C1)
CONSTRAINT INTEG_7:
  Unique key (C2)
CONSTRAINT TEST:
  Unique key (C3)
CONSTRAINT INTEG_9:
  CHECK (c2>c1)
CONSTRAINT TEST3:
  CHECK (NOT c3>c1)
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

