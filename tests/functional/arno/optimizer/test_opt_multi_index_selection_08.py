#coding:utf-8
#
# id:           functional.arno.optimizer.opt_multi_index_selection_08
# title:        Best match index selection (multi segment)
# decription:   STARTING WITH can also use a index and it should in fact be possible to use a compound index. Of course the STARTING WITH conjunction can only be bound the end (of all possible matches, same as >, >=, <, <=).
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_multi_index_selection_08

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
      ((:FillID / 100) * 100,
       :FILLID - ((:FillID / 100) * 100));
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
CREATE ASC INDEX I_F2_F1_ASC ON SelectionTest (F2, F1);
CREATE DESC INDEX I_F2_F1_DESC ON SelectionTest (F2, F1);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  st.F1, st.F2
FROM
  SelectionTest st
WHERE
  st.F1 = 100 and
  st.F2 STARTING WITH '55';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (ST INDEX (I_F1_F2_ASC))

          F1 F2
============ ==================

         100 55
"""

@pytest.mark.version('>=2.0')
def test_opt_multi_index_selection_08_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

