#coding:utf-8

"""
ID:          optimizer.inner-join-03
TITLE:       INNER JOIN join order
DESCRIPTION:
  With a INNER JOIN the relation with the smallest expected result should be the first one
  in process order. The next relation should be the next relation with expected smallest
  result based on previous relation and do on till last relation.

  Before 2.0, Firebird did stop checking order possibilties above 7 relations.
FBTEST:      functional.arno.optimizer.opt_inner_join_03
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_1 (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_1K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_2K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_3K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_4K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_5K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_6K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_8K (
  ID INTEGER NOT NULL
);

CREATE TABLE Table_10K (
  ID INTEGER NOT NULL
);

SET TERM ^^ ;
CREATE PROCEDURE PR_FillTable_10K
AS
DECLARE VARIABLE FillID INTEGER;
BEGIN
  FillID = 1;
  WHILE (FillID <= 10000) DO
  BEGIN
    INSERT INTO Table_10K (ID) VALUES (:FillID);
    FillID = FillID + 1;
  END
END
^^
SET TERM ; ^^

COMMIT;

INSERT INTO Table_1 (ID) VALUES (1);
EXECUTE PROCEDURE PR_FillTable_10K;
INSERT INTO Table_1K (ID) SELECT ID FROM Table_10K WHERE ID <= 1000;
INSERT INTO Table_2K (ID) SELECT ID FROM Table_10K WHERE ID <= 2000;
INSERT INTO Table_3K (ID) SELECT ID FROM Table_10K WHERE ID <= 3000;
INSERT INTO Table_4K (ID) SELECT ID FROM Table_10K WHERE ID <= 4000;
INSERT INTO Table_5K (ID) SELECT ID FROM Table_10K WHERE ID <= 5000;
INSERT INTO Table_6K (ID) SELECT ID FROM Table_10K WHERE ID <= 6000;
INSERT INTO Table_8K (ID) SELECT ID FROM Table_10K WHERE ID <= 8000;

COMMIT;

CREATE UNIQUE ASC INDEX PK_Table_1 ON Table_1 (ID);
CREATE UNIQUE ASC INDEX PK_Table_1K ON Table_1K (ID);
CREATE UNIQUE ASC INDEX PK_Table_2K ON Table_2K (ID);
CREATE UNIQUE ASC INDEX PK_Table_3K ON Table_3K (ID);
CREATE UNIQUE ASC INDEX PK_Table_4K ON Table_4K (ID);
CREATE UNIQUE ASC INDEX PK_Table_5K ON Table_5K (ID);
CREATE UNIQUE ASC INDEX PK_Table_6K ON Table_6K (ID);
CREATE UNIQUE ASC INDEX PK_Table_8K ON Table_8K (ID);
CREATE UNIQUE ASC INDEX PK_Table_10K ON Table_10K (ID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  Count(*)
FROM
  Table_5K t5K
  JOIN Table_6K t6K ON (t6K.ID = t5K.ID)
  JOIN Table_8K t8K ON (t8K.ID = t6K.ID)
  JOIN Table_10K t10K ON (t10K.ID = t8K.ID)
  JOIN Table_3K t3K ON (t3K.ID = t10K.ID)
  JOIN Table_4K t4K ON (t4K.ID = t3K.ID)
  JOIN Table_1K t1K ON (t1K.ID = t4K.ID)
  JOIN Table_2K t2K ON (t2K.ID = t1K.ID)
JOIN Table_1 t1 ON (t1.ID = t2K.ID);"""

act = isql_act('db', test_script, substitutions=[('=.*', '')])

# version: 3.0

expected_stdout_1 = """PLAN JOIN (T1 NATURAL, T1K INDEX (PK_TABLE_1K), T2K INDEX (PK_TABLE_2K), T3K INDEX (PK_TABLE_3K), T5K INDEX (PK_TABLE_5K), T4K INDEX (PK_TABLE_4K), T6K INDEX (PK_TABLE_6K), T8K INDEX (PK_TABLE_8K), T10K INDEX (PK_TABLE_10K))

       COUNT
============

1
"""

@pytest.mark.version('>=3,<4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """PLAN JOIN (T1 NATURAL, T1K INDEX (PK_TABLE_1K), T2K INDEX (PK_TABLE_2K), T3K INDEX (PK_TABLE_3K), T4K INDEX (PK_TABLE_4K), T5K INDEX (PK_TABLE_5K), T6K INDEX (PK_TABLE_6K), T8K INDEX (PK_TABLE_8K), T10K INDEX (PK_TABLE_10K))

       COUNT
============

1
"""

@pytest.mark.version('>=4')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
