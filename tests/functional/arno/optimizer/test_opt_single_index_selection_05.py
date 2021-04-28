#coding:utf-8
#
# id:           functional.arno.optimizer.opt_single_index_selection_05
# title:        Best match index selection (single segment) ASC and DESC
# decription:   Check if it will select the indexes which can be used. Also prefer ASC index above DESC unique index.
#               Index selectivity difference factor 20 and 200.
#               
#               selectivity = (1 / (count - duplicates));
#               
#               best = 0.001
#               999 / 20 = 49, 0..49 = 50 different values, = 0.02
#               999 / 200 = 4, 0..4 = 5 different values, = 0.2
#               
#               In FB2.0 there isn't a selectivity factor anymore, but index are based on there "total cost".
#               The cost for index F1 and F2 together is the best total cost.
#               
#               Cost = (data-pages * totalSelectivity) + total index cost.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_single_index_selection_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
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
CREATE DESC INDEX I_F1_DESC ON SelectionTest (F1);
CREATE DESC INDEX I_F2_DESC ON SelectionTest (F2);
CREATE DESC INDEX I_F3_DESC ON SelectionTest (F3);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  st.F1, st.F2, st.F3
FROM
  SelectionTest st
WHERE
  st.F1 = 200 and
  st.F2 = 200 and
  st.F3 = 200;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (ST INDEX (I_F1_ASC))

          F1           F2           F3
============ ============ ============

         200          200          200
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

