#coding:utf-8

"""
ID:          optimizer.mixed-joins-02
TITLE:       Mixed JOINS
DESCRIPTION:
  Tables without indexes should be merged (when inner join) and those who can use a index, should use it.
FBTEST:      functional.arno.optimizer.opt_mixed_joins_02

NOTES:
    [08.04.2022] pzotov
    FB 5.0.0.455 and later: data source with greatest cardinality will be specified at left-most position
    in the plan when HASH JOIN is choosen. Because of this, two cases of expected stdout must be taken
    in account, see variables 'fb3x_checked_stdout' and 'fb5x_checked_stdout'.
    See letter from dimitr, 05.04.2022 17:38.
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

COMMIT;

EXECUTE PROCEDURE PR_FillTable_10;
EXECUTE PROCEDURE PR_FillTable_100;
EXECUTE PROCEDURE PR_FillTable_1000;

COMMIT;

CREATE UNIQUE ASC INDEX PK_Table_100 ON Table_100 (ID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """
set planonly;
select count(*)
from table_1000 t1000
    left join table_100 t100 on (t100.id = t1000.id)
    join table_10 t10 on (t10.id = t100.id);
"""

act = isql_act('db', test_script)


fb3x_checked_stdout = """
    PLAN HASH (T10 NATURAL, JOIN (T1000 NATURAL, T100 INDEX (PK_TABLE_100)))
"""

fb5x_checked_stdout = """
    PLAN HASH (JOIN (T1000 NATURAL, T100 INDEX (PK_TABLE_100)), T10 NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = fb3x_checked_stdout if act.is_version('<5') else fb5x_checked_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
