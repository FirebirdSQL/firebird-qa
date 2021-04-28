#coding:utf-8
#
# id:           functional.arno.optimizer.opt_multi_index_selection_05
# title:        Best match index selection (multi segment)
# decription:   Check if it will select the index with the best selectivity and with the biggest segment match.
#               2 equals operators and 1 greater or equal operator and every index combination is made (only ASC). The best here is using 1 index (F2_F3_F1 or F3_F2_F1).
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_multi_index_selection_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE SelectionTest (
  F1 INTEGER NOT NULL,
  F2 INTEGER,
  F3 INTEGER
);

SET TERM ^^ ;
CREATE PROCEDURE PR_SelectionTest
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 1000) DO
  BEGIN
    INSERT INTO SelectionTest
      (F1, F2, F3)
    VALUES
      (:FillID, (:FILLID / 2) * 2, :FILLID);
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
CREATE UNIQUE ASC INDEX I_F1_UNIQUE_ASC ON SelectionTest (F1);
CREATE ASC INDEX I_F1_ASC ON SelectionTest (F1);
CREATE ASC INDEX I_F2_ASC ON SelectionTest (F2);
CREATE ASC INDEX I_F3_ASC ON SelectionTest (F3);
CREATE ASC INDEX I_F1_F2_ASC ON SelectionTest (F1, F2);
CREATE ASC INDEX I_F1_F3_ASC ON SelectionTest (F1, F3);
CREATE ASC INDEX I_F1_F2_F3_ASC ON SelectionTest (F1, F2, F3);
CREATE ASC INDEX I_F1_F3_F2_ASC ON SelectionTest (F1, F3, F2);
CREATE ASC INDEX I_F2_F1_ASC ON SelectionTest (F2, F1);
CREATE ASC INDEX I_F2_F3_ASC ON SelectionTest (F2, F3);
CREATE ASC INDEX I_F2_F1_F3_ASC ON SelectionTest (F2, F1, F3);
CREATE ASC INDEX I_F2_F3_F1_ASC ON SelectionTest (F2, F3, F1);
CREATE ASC INDEX I_F3_F1_ASC ON SelectionTest (F3, F1);
CREATE ASC INDEX I_F3_F2_ASC ON SelectionTest (F3, F2);
CREATE ASC INDEX I_F3_F1_F2_ASC ON SelectionTest (F3, F1, F2);
CREATE ASC INDEX I_F3_F2_F1_ASC ON SelectionTest (F3, F2, F1);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  st.F1, st.F2, st.F3
FROM
  SelectionTest st
WHERE
  st.F1 >= 1 and
  st.F2 = 100 and
  st.F3 = 100;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (ST INDEX (I_F3_F2_F1_ASC))

          F1           F2           F3
============ ============ ============

         100          100          100
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

