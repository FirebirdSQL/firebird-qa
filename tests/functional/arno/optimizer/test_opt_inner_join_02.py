#coding:utf-8
#
# id:           functional.arno.optimizer.opt_inner_join_02
# title:        INNER JOIN join order
# decription:   With a INNER JOIN the table with the smallest expected result should be the first one in process order.
#               When all tables have the same avg. recordsize (recordformat) the next table should be the second smallest.
#               Note that calculation is based on page-size. Thus for tables which use the same nr. of data-pages, but have in reality different nr. of records the table N could be bigger as table N+1 in the order.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_inner_join_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_10 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_100 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_3K (
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

CREATE PROCEDURE PR_FillTable_3K
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 3000) DO
  BEGIN
    INSERT INTO Table_3K (ID) VALUES (:FillID);
    FillID = FillID + 1;
  END
END
^^
SET TERM ; ^^

COMMIT;

EXECUTE PROCEDURE PR_FillTable_10;
EXECUTE PROCEDURE PR_FillTable_100;
EXECUTE PROCEDURE PR_FillTable_3K;

COMMIT;

CREATE UNIQUE ASC INDEX PK_Table_10 ON Table_10 (ID);
CREATE UNIQUE ASC INDEX PK_Table_100 ON Table_100 (ID);
CREATE UNIQUE ASC INDEX PK_Table_3K ON Table_3K (ID);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  Count(*)
FROM
  Table_3K t3K
  JOIN Table_100 t100 ON (t100.ID = t3K.ID)
  JOIN Table_10 t10 ON (t10.ID = t100.ID);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (T10 NATURAL, T100 INDEX (PK_TABLE_100), T3K INDEX (PK_TABLE_3K))

                COUNT
=====================
                   10

"""

@pytest.mark.version('>=3.0')
def test_opt_inner_join_02_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

