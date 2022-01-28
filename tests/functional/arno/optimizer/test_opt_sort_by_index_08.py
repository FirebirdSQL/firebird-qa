#coding:utf-8

"""
ID:          optimizer.sort-by-index-08
TITLE:       MIN() and DESC index (non-unique)
DESCRIPTION:
  SELECT MIN(FieldX) FROM X
  DESC index cannot be used for MIN() aggregate function.
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_66 (
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

CREATE DESC INDEX I_Table_66_DESC ON Table_66 (ID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  MIN(t66.ID) AS MIN_ID
FROM
Table_66 t66;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (T66 NATURAL)

      MIN_ID
============

-2147483648"""

@pytest.mark.version('>=2.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
