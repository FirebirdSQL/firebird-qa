#coding:utf-8
#
# id:           functional.arno.optimizer.opt_multi_index_selection_02
# title:        Best match index selection (multi segment)
# decription:   Check if it will select the indexes which can be used.
#               (Indexes with selectivity more than 10x the best are ignored)
#               See SELECTIVITY_THRESHOLD_FACTOR in opt.cpp
#               
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_multi_index_selection_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE SelectionTest (
  F1 INTEGER NOT NULL,
  F2 INTEGER NOT NULL,
  F3 INTEGER NOT NULL
);

SET TERM ^^ ;
CREATE PROCEDURE PR_SelectionTest
AS
DECLARE VARIABLE FillID INTEGER;
DECLARE VARIABLE FillF1 INTEGER;
DECLARE VARIABLE FillF2 INTEGER;
DECLARE VARIABLE FillF3 INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 999) DO
  BEGIN
    FILLF1 = (FILLID / 10) * 10;
    FILLF2 = FILLID - FILLF1;
    FILLF3 = (FILLID / 150) * 150;
    INSERT INTO SelectionTest
      (F1, F2, F3)
    VALUES
      (:FILLF1, :FILLF2, :FILLF3);
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
CREATE ASC INDEX I_F1_F2_ASC ON SelectionTest (F1, F2);
CREATE ASC INDEX I_F3_F2_ASC ON SelectionTest (F3, F2);
CREATE ASC INDEX I_F1_ASC ON SelectionTest (F1);
CREATE ASC INDEX I_F3_ASC ON SelectionTest (F3);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  st.F1, st.F2, st.F3
FROM
  SelectionTest st
WHERE
  st.F1 = 150 and
  st.F2 = 0 and
  st.F3 = 150;

/*
SELECT
  i.RDB$INDEX_NAME AS INDEX_NAME,
  CAST(i.RDB$STATISTICS AS NUMERIC(18,5)) AS SELECTIVITY
FROM
  RDB$INDICES i
WHERE
  i.RDB$RELATION_NAME = 'SELECTIONTEST';
*/"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (ST INDEX (I_F1_F2_ASC))

          F1           F2           F3
============ ============ ============

         150            0          150
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

