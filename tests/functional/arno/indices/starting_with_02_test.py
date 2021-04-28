#coding:utf-8
#
# id:           functional.arno.indices.starting_with_02
# title:        STARTING WITH charset ISO8859_1
# decription:   STARTING WITH - Select from table with 2 entries
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.indexes.starting_with_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE A_TEST (F1 VARCHAR(5), F2 VARCHAR(5), F3 VARCHAR(5));
CREATE INDEX IDX_A_TEST_F1 ON A_TEST(F1);
CREATE DESC INDEX IDX_A_TEST_F2 ON A_TEST(F2);
COMMIT;
INSERT INTO A_TEST (F1, F2, F3) VALUES('', '', '');
INSERT INTO A_TEST (F1, F2, F3) VALUES(NULL, NULL, NULL);
INSERT INTO A_TEST (F1, F2, F3) VALUES('a', 'a', 'a');
INSERT INTO A_TEST (F1, F2, F3) VALUES('b', 'b', 'b');
COMMIT;

SET TERM ^;

CREATE PROCEDURE PR_A_TEST_STARTING_WITH(I_START_VALUE VARCHAR(5))
RETURNS(O_FIELD VARCHAR(32), O_COUNT integer)
AS
BEGIN
  /* First retrieve results for indexed ASC field */
  O_FIELD = 'F1 - INDEXED ASC';
  SELECT COUNT(*) FROM A_TEST
  WHERE F1 STARTING WITH :I_START_VALUE
  INTO :O_COUNT;

  SUSPEND;

  /* Second retrieve results for indexed DESC field */
  O_FIELD = 'F2 - INDEXED DESC';
  SELECT COUNT(*) FROM A_TEST
  WHERE F2 STARTING WITH :I_START_VALUE
  INTO :O_COUNT;

  SUSPEND;

  /* Thirth for unindexed field */
  O_FIELD = 'F3 - NOT INDEXED';
  SELECT COUNT(*) FROM A_TEST
  WHERE F3 STARTING WITH :I_START_VALUE
  INTO :O_COUNT;

  SUSPEND;
END^

SET TERM ;^

"""

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN OFF;
SELECT O_FIELD, O_COUNT FROM PR_A_TEST_STARTING_WITH('');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """O_FIELD                               O_COUNT
================================ ============

F1 - INDEXED ASC                            3
F2 - INDEXED DESC                           3
F3 - NOT INDEXED                            3"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

