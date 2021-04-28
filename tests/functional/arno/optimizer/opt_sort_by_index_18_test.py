#coding:utf-8
#
# id:           functional.arno.optimizer.opt_sort_by_index_18
# title:        ORDER BY ASC using index (single) and WHERE clause
# decription:   WHERE X = 1 ORDER BY Y
#               Index for both X and Y should be used when available.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_sort_by_index_18

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_53 (
  ID1 INTEGER,
  ID2 INTEGER
);

SET TERM ^^ ;
CREATE PROCEDURE PR_FillTable_53
AS
DECLARE VARIABLE FillID INTEGER;
DECLARE VARIABLE FillID1 INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 50) DO
  BEGIN
    FillID1 = (FillID / 10) * 10;
    INSERT INTO Table_53
      (ID1, ID2)
    VALUES
      (:FillID1, :FillID - :FillID1);
    FillID = FillID + 1;
  END
  INSERT INTO Table_53 (ID1, ID2) VALUES (0, NULL);
  INSERT INTO Table_53 (ID1, ID2) VALUES (NULL, 0);
  INSERT INTO Table_53 (ID1, ID2) VALUES (NULL, NULL);
END
^^
SET TERM ; ^^

COMMIT;

EXECUTE PROCEDURE PR_FillTable_53;

COMMIT;

CREATE ASC INDEX I_Table_53_ID1_ASC ON Table_53 (ID1);
CREATE DESC INDEX I_Table_53_ID1_DESC ON Table_53 (ID1);
CREATE ASC INDEX I_Table_53_ID2_ASC ON Table_53 (ID2);
CREATE DESC INDEX I_Table_53_ID2_DESC ON Table_53 (ID2);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  t53.ID2,
  t53.ID1
FROM
  Table_53 t53
WHERE
  t53.ID1 = 30
ORDER BY
  t53.ID2 ASC;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (T53 ORDER I_TABLE_53_ID2_ASC INDEX (I_TABLE_53_ID1_ASC))

         ID2          ID1
============ ============

           0           30
           1           30
           2           30
           3           30
           4           30
           5           30
           6           30
           7           30
           8           30
           9           30
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

