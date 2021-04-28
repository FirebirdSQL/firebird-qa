#coding:utf-8
#
# id:           functional.arno.optimizer.opt_inner_join_07
# title:        INNER JOIN join order and VIEW
# decription:   With a INNER JOIN the relation with the smallest expected result should be the first one in process order. The next relation should be the next relation with expected smallest result based on previous relation and do on till last relation.
#               
#               Old/Current limitation in Firebird does stop checking order possibilties above 7 relations.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_inner_join_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """CREATE TABLE Table_1 (
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

CREATE VIEW View_A (
  ID1K,
  ID6K
)
AS
SELECT
  t1K.ID,
  t6K.ID
FROM
  Table_6K t6K
  JOIN Table_1K t1K ON (t1K.ID = t6K.ID);

CREATE VIEW View_B (
  ID3K,
  ID10K
)
AS
SELECT
  t3K.ID,
  t10K.ID
FROM
  Table_3K t3K
  JOIN Table_10K t10K ON (t10K.ID = t3K.ID);

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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  Count(*)
FROM
  View_B vb
  JOIN View_A va ON (va.ID1K = vb.ID10K);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (VA T1K NATURAL, VB T3K INDEX (PK_TABLE_3K), VA T6K INDEX (PK_TABLE_6K), VB T10K INDEX (PK_TABLE_10K))


       COUNT
============

        1000
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

