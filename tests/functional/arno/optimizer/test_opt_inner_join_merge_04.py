#coding:utf-8

"""
ID:          optimizer.inner-join-merge-04
TITLE:       INNER JOIN join merge and NULLs
DESCRIPTION:
  X JOIN Y ON (X.Field = Y.Field)
  When no index can be used on a INNER JOIN and there's a relation setup between X and Y
  then a MERGE should be performed. An equality between NULLs should not be seen as true.
FBTEST:      functional.arno.optimizer.opt_inner_join_merge_04
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_10 (
  ID INTEGER
);

CREATE TABLE Table_100 (
  ID INTEGER
);

SET TERM ^^ ;
CREATE PROCEDURE PR_FillTable_10
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 15) DO
  BEGIN
    IF (FillID <= 10) THEN
    BEGIN
      INSERT INTO Table_10 (ID) VALUES (:FillID);
    END ELSE BEGIN
      INSERT INTO Table_10 (ID) VALUES (NULL);
    END
    FillID = FillID + 1;
  END
END
^^

CREATE PROCEDURE PR_FillTable_100
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 110) DO
  BEGIN
    IF (FillID <= 100) THEN
    BEGIN
      INSERT INTO Table_100 (ID) VALUES (:FillID);
    END ELSE BEGIN
      INSERT INTO Table_100 (ID) VALUES (NULL);
    END
    FillID = FillID + 1;
  END
END
^^
SET TERM ; ^^

COMMIT;

EXECUTE PROCEDURE PR_FillTable_10;
EXECUTE PROCEDURE PR_FillTable_100;

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  Count(*)
FROM
  Table_100 t100
JOIN Table_10 t10 ON (t10.ID = t100.ID);"""

act = isql_act('db', test_script)

expected_stdout = """PLAN HASH (T100 NATURAL, T10 NATURAL)

                COUNT
=====================
                   10
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
