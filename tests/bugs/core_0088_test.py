#coding:utf-8
#
# id:           bugs.core_0088
# title:        Join on diffrent datatypes
# decription:
# tracker_id:   CORE-88
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_88

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST_A (
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;

SELECT * FROM test_b WHERE num NOT IN (SELECT snum FROM test_a) ;

SELECT * FROM test_b WHERE num IN (SELECT snum FROM test_a) ;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

