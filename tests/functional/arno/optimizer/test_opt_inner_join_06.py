#coding:utf-8

"""
ID:          optimizer.inner-join-06
TITLE:       INNER JOIN join order and VIEW
DESCRIPTION:
  With a INNER JOIN the table with the smallest expected result should be the first one in
  process order. All inner joins are combined to 1 inner join, because then a order can be
  decided between them. Relations from a VIEW can also be "merged" to the 1 inner join
  (of course not with outer joins/unions/etc..)
FBTEST:      functional.arno.optimizer.opt_inner_join_06
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_10 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_100 (
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
SET TERM ; ^^

CREATE VIEW View_10 (
  ID
)
AS
SELECT
  ID
FROM
  Table_10;

CREATE VIEW View_100 (
  ID
)
AS
SELECT
  ID
FROM
  Table_100;

COMMIT;

EXECUTE PROCEDURE PR_FillTable_10;
EXECUTE PROCEDURE PR_FillTable_100;

COMMIT;

CREATE UNIQUE ASC INDEX PK_Table_10 ON Table_10 (ID);
CREATE UNIQUE ASC INDEX PK_Table_100 ON Table_100 (ID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  Count(*)
FROM
  View_100 v100
JOIN View_10 v10 ON (v10.ID = v100.ID);"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (V10 TABLE_10 NATURAL, V100 TABLE_100 INDEX (PK_TABLE_100))

                COUNT
=====================
                   10
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
