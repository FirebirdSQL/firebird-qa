#coding:utf-8

"""
ID:          optimizer.single-index-selection-04
TITLE:       Best match index selection (single segment)
DESCRIPTION:
    Check if it will select the indexes which can be used.
    Index selectivity difference factor 20 and 200.
    (Indexes with selectivity more than 10x the best are ignored)
    See SELECTIVITY_THRESHOLD_FACTOR in opt.cpp

    selectivity = (1 / (count - duplicates));

    best = 0.001
    999 / 20 = 49, 0..49 = 50 different values, = 0.02
    999 / 200 = 4, 0..4 = 5 different values, = 0.2
FBTEST:      functional.arno.optimizer.opt_single_index_selection_04
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE SelectionTest (
  F1 INTEGER NOT NULL,
  F2 INTEGER NOT NULL,
  F3 INTEGER NOT NULL
);

SET TERM ^^ ;
CREATE PROCEDURE PR_SelectionTest
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 999) DO
  BEGIN
    INSERT INTO SelectionTest
      (F1, F2, F3)
    VALUES
      (:FILLID,
       (:FILLID / 20) * 20,
       (:FILLID / 200) * 200);
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
CREATE ASC INDEX I_F2_ASC ON SelectionTest (F2);
CREATE ASC INDEX I_F3_ASC ON SelectionTest (F3);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  st.F1, st.F2, st.F3
FROM
  SelectionTest st
WHERE
  st.F1 = 200 and
  st.F2 = 200 and
  st.F3 = 200;
"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (ST INDEX (I_F1_ASC))

          F1           F2           F3
============ ============ ============

         200          200          200
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
