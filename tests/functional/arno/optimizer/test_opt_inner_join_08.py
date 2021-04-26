#coding:utf-8
#
# id:           functional.arno.optimizer.opt_inner_join_08
# title:        INNER JOIN join order and VIEW
# decription:   Try to merge the top INNER JOINs of VIEWS/TABLES together to 1 inner join.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_inner_join_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_1 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_50 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_100 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_250 (
  ID INTEGER NOT NULL
);

SET TERM ^^ ;
CREATE PROCEDURE PR_FillTable_50
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 50) DO
  BEGIN
    INSERT INTO Table_50 (ID) VALUES (:FillID);
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

CREATE PROCEDURE PR_FillTable_250
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 250) DO
  BEGIN
    INSERT INTO Table_250 (ID) VALUES (:FillID);
    FillID = FillID + 1;
  END
END
^^
SET TERM ; ^^


CREATE VIEW View_A (
  ID1,
  ID250
)
AS
SELECT
  t1.ID,
  t250.ID
FROM
  Table_1 t1
  LEFT JOIN Table_250 t250 ON (t250.ID = t1.ID);

CREATE VIEW View_B (
  ID50,
  ID100
)
AS
SELECT
  t50.ID,
  t100.ID
FROM
  Table_50 t50
  JOIN Table_100 t100 ON (t100.ID = t50.ID);

COMMIT;

INSERT INTO Table_1 (ID) VALUES (1);
EXECUTE PROCEDURE PR_FillTable_50;
EXECUTE PROCEDURE PR_FillTable_100;
EXECUTE PROCEDURE PR_FillTable_250;

COMMIT;

CREATE UNIQUE ASC INDEX PK_Table_1 ON Table_1 (ID);
CREATE UNIQUE ASC INDEX PK_Table_50 ON Table_50 (ID);
CREATE UNIQUE ASC INDEX PK_Table_100 ON Table_100 (ID);
CREATE UNIQUE ASC INDEX PK_Table_250 ON Table_250 (ID);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  Count(*)
FROM
  View_B vb
  JOIN View_A va ON (va.ID1 = vb.ID100);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (JOIN (VA T1 NATURAL, VA T250 INDEX (PK_TABLE_250)), JOIN (VB T50 INDEX (PK_TABLE_50), VB T100 INDEX (PK_TABLE_100)))

                COUNT
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_opt_inner_join_08_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

