#coding:utf-8
#
# id:           functional.arno.derived_tables.derived_tables_16
# title:        Simple derived table
# decription:   Test aggregate inside derived table.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.derived_tables.derived_tables_16

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
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
  (SELECT t1.GROUPID, Count(t1.ID) FROM Table_10 t1 GROUP BY t1.GROUPID) dt (GROUPID, ID_COUNT);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """     GROUPID              ID_COUNT
============ =====================
      <null>                     1
           1                     2
           2                     3
           3                     4

"""

@pytest.mark.version('>=3.0')
def test_derived_tables_16_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

