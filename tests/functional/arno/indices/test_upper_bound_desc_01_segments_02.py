#coding:utf-8

"""
ID:          index.upper-bound-desc-1-segment-02
TITLE:       DESC single segment index upper bound
DESCRIPTION: Check if all 15 values are fetched with "greater than" operator.
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
  ID
FROM
  Table_66 t66
WHERE
t66.ID > 131071;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (T66 INDEX (I_TABLE_66_DESC))

          ID
============

  2147483647
  1073741823
   536870911
   268435455
   134217727
    67108863
    33554431
    16777215
     8388607
     4194303
     2097151
     1048575
      524287
262143"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
