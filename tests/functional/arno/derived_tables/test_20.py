#coding:utf-8
#
# id:           functional.arno.derived_tables.20
# title:        Simple derived table
# decription:   Test sub-select inside derived table.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.derived_tables.derived_tables_20

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_10 (
  ID INTEGER NOT NULL,
  GROUPID INTEGER,
  DESCRIPTION VARCHAR(10)
);

COMMIT;

INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (0, NULL, NULL);
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (1, 1, 'one');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (2, 1, 'two');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (3, 2, 'three');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (4, 2, 'four');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (5, 2, 'five');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (6, 3, 'six');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (7, 3, 'seven');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (8, 3, 'eight');
INSERT INTO Table_10 (ID, GROUPID, DESCRIPTION) VALUES (9, 3, 'nine');

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT
  dt.*
FROM
  (SELECT
    t2.GROUPID,
    (SELECT MIN(t1.ID) FROM Table_10 t1 WHERE t1.GROUPID = t2.GROUPID),
    (SELECT MAX(t1.ID) FROM Table_10 t1 WHERE t1.GROUPID = t2.GROUPID)
   FROM
     Table_10 t2
   GROUP BY
t2.GROUPID) dt (GROUPID, MIN_ID, MAX_ID);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """     GROUPID       MIN_ID       MAX_ID
============ ============ ============
      <null>       <null>       <null>
           1            1            2
           2            3            5
3            6            9"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

