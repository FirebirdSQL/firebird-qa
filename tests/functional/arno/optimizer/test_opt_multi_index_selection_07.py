#coding:utf-8

"""
ID:          optimizer.multi-index-selection-06
TITLE:       Best match index selection (multi segment)
DESCRIPTION:
  Check if it will select the index with the best selectivity and match.
  IS NULL should also be used in compound indexes.
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

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  st.F1, st.F2
FROM
  SelectionTest st
WHERE
  st.F1 = 55 and
st.F2 IS NULL;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (ST INDEX (I_F1_F2_ASC))

          F1           F2
============ ============

          55       <null>
          55       <null>
          55       <null>
          55       <null>
55       <null>"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
