#coding:utf-8

"""
ID:          optimizer.inner-join-merge-06
TITLE:       INNER JOIN join merge and SP
DESCRIPTION:
  X JOIN Y ON (X.Field = Y.Field)
  When no index can be used on a INNER JOIN and there's a relation setup between X and Y
  then a MERGE should be performed. Test with selectable Stored Procedure.
FBTEST:      functional.arno.optimizer.opt_inner_join_merge_06
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

CREATE PROCEDURE PR_List_1000
RETURNS (
  ID Integer
)
AS
BEGIN
  ID = 2;
  WHILE (ID <= 1000) DO
  BEGIN
    SUSPEND;
    ID = ID + 2;
  END
END
^^
SET TERM ; ^^

COMMIT;

EXECUTE PROCEDURE PR_FillTable_10;
EXECUTE PROCEDURE PR_FillTable_100;

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """
    set planonly;
    select count(*)
    from table_100 t100
    join table_10 t10 on (t10.id = t100.id)
    join pr_list_1000 sp1000 on (sp1000.id = t10.id);
"""

act = isql_act('db', test_script)

fb3x_checked_stdout = """
    PLAN HASH (T100 NATURAL, T10 NATURAL, SP1000 NATURAL)
"""

fb5x_checked_stdout = """
    PLAN HASH (SP1000 NATURAL, T10 NATURAL, T100 NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    with act.connect_server() as srv:
        engine_major = int(srv.info.engine_version)

    act.expected_stdout = fb3x_checked_stdout if engine_major < 5 else fb5x_checked_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
