#coding:utf-8
#
# id:           functional.arno.optimizer.opt_multi_index_selection_07
# title:        Best match index selection (multi segment)
# decription:   Check if it will select the index with the best selectivity and match.
#               IS NULL should also be used in compound indexes (Only in new index structure ODS > FB 1.5.1)
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_multi_index_selection_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE SelectionTest (
  F1 INTEGER NOT NULL,
  F2 INTEGER
);

SET TERM ^^ ;
CREATE PROCEDURE PR_SelectionTest
AS
DECLARE VARIABLE FillID INTEGER;
DECLARE VARIABLE FillF2 INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 1000) DO
  BEGIN

    IF (FillID <= 100) THEN
    BEGIN
      FillF2 = NULL;
    END ELSE BEGIN
      FillF2 = FillID - 100;
    END

    INSERT INTO SelectionTest
      (F1, F2)
    VALUES
      ((:FillID / 5) * 5, :FILLF2);
    FillID = FillID + 1;
  END
END
^^
SET TERM ; ^^

COMMIT;

/* Fill table with data */
EXECUTE PROCEDURE PR_SelectionTest;

COMMIT;

/* Create indexes */
CREATE ASC INDEX I_F1_ASC ON SelectionTest (F1);
CREATE DESC INDEX I_F1_DESC ON SelectionTest (F1);
CREATE ASC INDEX I_F2_ASC ON SelectionTest (F2);
CREATE DESC INDEX I_F2_DESC ON SelectionTest (F2);
CREATE ASC INDEX I_F1_F2_ASC ON SelectionTest (F1, F2);
CREATE DESC INDEX I_F1_F2_DESC ON SelectionTest (F1, F2);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  st.F1, st.F2
FROM
  SelectionTest st
WHERE
  st.F1 = 55 and
  st.F2 IS NULL;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (ST INDEX (I_F1_F2_ASC))

          F1           F2
============ ============

          55       <null>
          55       <null>
          55       <null>
          55       <null>
          55       <null>
"""

@pytest.mark.version('>=2.0')
def test_opt_multi_index_selection_07_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

