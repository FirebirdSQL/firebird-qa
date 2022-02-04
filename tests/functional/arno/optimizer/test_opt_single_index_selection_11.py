#coding:utf-8

"""
ID:          optimizer.single-index-selection-10
TITLE:       Best match index selection (single segment)
DESCRIPTION:
  Check if it will select the best index.
  IS NULL can return more records thus prefer equal.
FBTEST:      functional.arno.optimizer.opt_single_index_selection_11
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE SelectionTest (
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
      (:FillID, :FILLF2);
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

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  st.F1, st.F2
FROM
  SelectionTest st
WHERE
  st.F2 IS NULL and
st.F1 = 55;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (ST INDEX (I_F1_UNIQUE_ASC))

          F1           F2
============ ============

55       <null>"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
