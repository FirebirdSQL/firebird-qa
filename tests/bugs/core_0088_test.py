#coding:utf-8

"""
ID:          issue-413
ISSUE:       413
TITLE:       Join on diffrent datatypes
DESCRIPTION:
JIRA:        CORE-88
FBTEST:      bugs.core_0088
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE TEST_A (
    ID INTEGER NOT NULL PRIMARY KEY,
    SNUM CHAR(10) UNIQUE
);

CREATE TABLE TEST_B (
    ID INTEGER NOT NULL PRIMARY KEY,
    NUM NUMERIC(15,2) UNIQUE
);

commit;

INSERT INTO TEST_A (ID, SNUM) VALUES (1, '01');
INSERT INTO TEST_A (ID, SNUM) VALUES (2, '02');
INSERT INTO TEST_A (ID, SNUM) VALUES (3, '03');
INSERT INTO TEST_A (ID, SNUM) VALUES (5, '05');

commit;

INSERT INTO TEST_B (ID, NUM) VALUES (1, 1);
INSERT INTO TEST_B (ID, NUM) VALUES (2, 2);
INSERT INTO TEST_B (ID, NUM) VALUES (3, 3);
INSERT INTO TEST_B (ID, NUM) VALUES (4, 4);

commit;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;

SELECT * FROM test_b WHERE num NOT IN (SELECT snum FROM test_a) ;

SELECT * FROM test_b WHERE num IN (SELECT snum FROM test_a) ;

"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (TEST_A NATURAL)
PLAN (TEST_A NATURAL)
PLAN (TEST_B NATURAL)

          ID                   NUM
============ =====================
           4                  4.00


PLAN (TEST_A NATURAL)
PLAN (TEST_B NATURAL)

          ID                   NUM
============ =====================
           1                  1.00
           2                  2.00
           3                  3.00

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

