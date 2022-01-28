#coding:utf-8
#
# id:           functional.arno.indices.upper_bound_asc_01_segments_01
# title:        ASC single index upper bound
# decription:   Check if all 15 values are fetched with "lower than or equal" operator.
# tracker_id:
# min_versions: []
# versions:     1.5
# qmid:         functional.arno.indexes.upper_bound_asc_01_segments_01

"""
ID:          index.upper-bound-asc-1-segment-01
TITLE:       ASC single segment index upper bound
DESCRIPTION: Check if all 15 values are fetched with "lower than or equal" operator.
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

CREATE ASC INDEX I_Table_66_ASC ON Table_66 (ID);

COMMIT;
"""

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
SELECT
  ID
FROM
  Table_66 t66
WHERE
t66.ID <= -131072;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (T66 INDEX (I_TABLE_66_ASC))

          ID
============

 -2147483648
 -1073741824
  -536870912
  -268435456
  -134217728
   -67108864
   -33554432
   -16777216
    -8388608
    -4194304
    -2097152
    -1048576
     -524288
     -262144
-131072"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
