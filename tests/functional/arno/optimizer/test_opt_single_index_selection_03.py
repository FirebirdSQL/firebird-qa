#coding:utf-8

"""
ID:          optimizer.single-index-selection-03
TITLE:       Best match index selection (single segment)
DESCRIPTION:
  Check if it will select the indexes which can be used.
  Also prefer ASC index above DESC unique index.
  Unique index isn't the only best to use here, because
  there's not a equals operator on it.
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
BEGIN
  FillID = 1;
  WHILE (FillID <= 1000) DO
  BEGIN
    INSERT INTO SelectionTest
      (F1, F2)
    VALUES
      (:FillID, (:FILLID / 2) * 2);
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
CREATE UNIQUE DESC INDEX I_F1_UNIQUE_DESC ON SelectionTest (F1);
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
  st.F2 = 100 and
st.F1 >= 1;"""

act = isql_act('db', test_script, substitutions=[('=.*', '')])

expected_stdout = """PLAN (ST INDEX (I_F2_ASC))

          F1           F2
============ ============
         100          100
         101          100
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
