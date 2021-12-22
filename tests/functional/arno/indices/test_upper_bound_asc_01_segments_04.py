#coding:utf-8
#
# id:           functional.arno.indices.upper_bound_asc_01_segments_04
# title:        ASC single index upper bound
# decription:   Check if all 5 values are fetched with "lower than or equal" operator.
# tracker_id:   
# min_versions: []
# versions:     1.5
# qmid:         functional.arno.indexes.upper_bound_asc_01_segments_04

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_A15 (
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  ID
FROM
  Table_A15 a15
WHERE
a15.ID < 'AAAB';"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (A15 INDEX (I_TABLE_A15_ASC))

ID
===============

A
AA
AAA
AAAA
AAAAB"""

@pytest.mark.version('>=1.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

