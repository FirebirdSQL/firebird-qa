#coding:utf-8
#
# id:           functional.arno.optimizer.opt_sort_by_index_06
# title:        MAX() and ASC index (non-unique)
# decription:   SELECT MAX(FieldX) FROM X
#               ASC index cannot be used for MAX() aggregate function.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_sort_by_index_06

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_66 (
  ID INTEGER
);

SET TERM ^^ ;
CREATE PROCEDURE PR_FillTable_66
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 2147483647;
  WHILE (FillID > 0) DO
  BEGIN
    INSERT INTO Table_66 (ID) VALUES (:FillID);
    FillID = FillID / 2;
  END
  INSERT INTO Table_66 (ID) VALUES (NULL);
  INSERT INTO Table_66 (ID) VALUES (0);
  INSERT INTO Table_66 (ID) VALUES (NULL);
  FillID = -2147483648;
  WHILE (FillID < 0) DO
  BEGIN
    INSERT INTO Table_66 (ID) VALUES (:FillID);
    FillID = FillID / 2;
  END
END
^^
SET TERM ; ^^

COMMIT;

EXECUTE PROCEDURE PR_FillTable_66;

COMMIT;

CREATE ASC INDEX I_Table_66_ASC ON Table_66 (ID);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  MAX(t66.ID) AS MAX_ID
FROM
  Table_66 t66;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (T66 NATURAL)

      MAX_ID
============

  2147483647
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

