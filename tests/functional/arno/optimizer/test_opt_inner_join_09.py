#coding:utf-8
#
# id:           functional.arno.optimizer.opt_inner_join_09
# title:        INNER JOIN join order and distribution
# decription:   With a INNER JOIN the relation with the smallest expected result should be the first one in process order. The next relation should be the next relation with expected smallest result based on previous relation and do on till last relation.
#               
#               Distribution is tested if it's conjunctions are distributed from WHERE clause.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_inner_join_09

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = [('=.*', '')]

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
  Table_50 t50
  JOIN Table_100 t100 ON (t100.ID = t50.ID)
  JOIN Table_1 t1 ON (1 = 1)
  JOIN Table_250 t250 ON (1 = 1)
WHERE
  t250.ID = t1.ID and
  t100.ID = t1.ID;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (T1 NATURAL, T50 INDEX (PK_TABLE_50), T100 INDEX (PK_TABLE_100), T250 INDEX (PK_TABLE_250))

       COUNT
============

           1
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

