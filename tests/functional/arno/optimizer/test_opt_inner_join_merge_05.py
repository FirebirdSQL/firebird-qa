#coding:utf-8

"""
ID:          optimizer.inner-join-merge-05
TITLE:       INNER JOIN join merge and VIEWs
DESCRIPTION:
  X JOIN Y ON (X.Field = Y.Field)
  When no index can be used on a INNER JOIN and there's a relation setup between X and Y
  then a MERGE should be performed. Of course also when a VIEW is used.
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_10 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_100 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_1000 (
  ID INTEGER NOT NULL
);

SET TERM ^^ ;
CREATE PROCEDURE PR_FillTable_10
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 10) DO
  BEGIN
    INSERT INTO Table_10 (ID) VALUES (:FillID);
    FillID = FillID + 1;
  END
END
^^

CREATE PROCEDURE PR_FillTable_100
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 100) DO
  BEGIN
    INSERT INTO Table_100 (ID) VALUES (:FillID);
    FillID = FillID + 1;
  END
END
^^

CREATE PROCEDURE PR_FillTable_1000
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 1000) DO
  BEGIN
    INSERT INTO Table_1000 (ID) VALUES (:FillID);
    FillID = FillID + 1;
  END
END
^^
SET TERM ; ^^

CREATE VIEW View_A (
  ID10,
  ID100
)
AS
SELECT
  t10.ID,
  t100.ID
FROM
  Table_100 t100
  JOIN Table_10 t10 ON (t10.ID = t100.ID);

COMMIT;

EXECUTE PROCEDURE PR_FillTable_10;
EXECUTE PROCEDURE PR_FillTable_100;
EXECUTE PROCEDURE PR_FillTable_1000;

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  Count(*)
FROM
  Table_1000 t1000
JOIN View_A va ON (va.ID100 = t1000.ID);"""

act = isql_act('db', test_script)

expected_stdout = """PLAN HASH (T1000 NATURAL, VA T100 NATURAL, VA T10 NATURAL)

                COUNT
=====================
                   10
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
