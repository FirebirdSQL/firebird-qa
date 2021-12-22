#coding:utf-8
#
# id:           functional.arno.optimizer.opt_single_index_selection_08
# title:        Best match index selection (single segment)
# decription:   Check if it will select the index with the best selectivity.
#               STARTING WITH can also use a index, but 1 index is enough and prefer ASC index.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_single_index_selection_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE SelectionTest (
  F1 INTEGER NOT NULL,
  F2 VARCHAR(18)
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
      (F1, F2)
    VALUES
      (:FillID, :FILLID);
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
CREATE DESC INDEX I_F1_DESC ON SelectionTest (F1);
CREATE ASC INDEX I_F2_ASC ON SelectionTest (F2);
CREATE DESC INDEX I_F2_DESC ON SelectionTest (F2);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  st.F1, st.F2
FROM
  SelectionTest st
WHERE
  st.F1 <= 49 and
st.F2 STARTING WITH '5';"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (ST INDEX (I_F2_ASC, I_F1_ASC))

          F1 F2
============ ==================

5 5"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

