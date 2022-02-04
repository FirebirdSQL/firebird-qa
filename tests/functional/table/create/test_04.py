#coding:utf-8

"""
ID:          table.create-04
TITLE:       CREATE TABLE - constraints
DESCRIPTION:
FBTEST:      functional.table.create.04
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE fk(id INT NOT NULL PRIMARY KEY);
commit;
"""

db = db_factory(init=init_script)

test_script = """CREATE TABLE test(
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
SHOW TABLE test;
"""

act = isql_act('db', test_script)

expected_stdout = """C1                              SMALLINT Not Null
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

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
