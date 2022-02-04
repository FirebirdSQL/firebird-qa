#coding:utf-8

"""
ID:          index.upper-bound-asc-1-segment-03
TITLE:       ASC single segment index upper bound
DESCRIPTION: Check if all 5 values are fetched with "lower than or equal" operator.
FBTEST:      functional.arno.indices.upper_bound_asc_01_segments_03
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_A15 (
  ID VARCHAR(15)
);

INSERT INTO Table_A15 (ID) VALUES (NULL);
INSERT INTO Table_A15 (ID) VALUES ('A');
INSERT INTO Table_A15 (ID) VALUES ('AA');
INSERT INTO Table_A15 (ID) VALUES ('AAA');
INSERT INTO Table_A15 (ID) VALUES ('AAAA');
INSERT INTO Table_A15 (ID) VALUES ('AAAAB');
INSERT INTO Table_A15 (ID) VALUES ('AAAB');
INSERT INTO Table_A15 (ID) VALUES ('AAB');
INSERT INTO Table_A15 (ID) VALUES ('AB');
INSERT INTO Table_A15 (ID) VALUES ('B');
INSERT INTO Table_A15 (ID) VALUES ('BA');
INSERT INTO Table_A15 (ID) VALUES ('BAA');
INSERT INTO Table_A15 (ID) VALUES ('BAAA');
INSERT INTO Table_A15 (ID) VALUES ('BAAAA');
INSERT INTO Table_A15 (ID) VALUES ('BAAAB');

COMMIT;

CREATE ASC INDEX I_Table_A15_ASC ON Table_A15 (ID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  ID
FROM
  Table_A15 a15
WHERE
a15.ID <= 'AAAAB';"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (A15 INDEX (I_TABLE_A15_ASC))

ID
===============

A
AA
AAA
AAAA
AAAAB"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
