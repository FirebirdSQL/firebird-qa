#coding:utf-8
#
# id:           functional.arno.optimizer.opt_sort_by_index_16
# title:        ORDER BY DESC NULLS FIRST using index
# decription:   ORDER BY X DESC NULLS FIRST
#               When a index can be used for sorting, use it.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_sort_by_index_16

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_66 (
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
CREATE DESC INDEX I_Table_66_DESC ON Table_66 (ID);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  ID
FROM
  Table_66 t66
ORDER BY
  t66.ID DESC NULLS FIRST;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN SORT (T66 NATURAL)

          ID
============
      <null>
      <null>
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
      262143
      131071
       65535
       32767
       16383

          ID
============
        8191
        4095
        2047
        1023
         511
         255
         127
          63
          31
          15
           7
           3
           1
           0
          -1
          -2
          -4
          -8
         -16
         -32

          ID
============
         -64
        -128
        -256
        -512
       -1024
       -2048
       -4096
       -8192
      -16384
      -32768
      -65536
     -131072
     -262144
     -524288
    -1048576
    -2097152
    -4194304
    -8388608
   -16777216
   -33554432

          ID
============
   -67108864
  -134217728
  -268435456
  -536870912
 -1073741824
 -2147483648

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

