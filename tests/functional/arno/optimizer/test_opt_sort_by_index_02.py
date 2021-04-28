#coding:utf-8
#
# id:           functional.arno.optimizer.opt_sort_by_index_02
# title:        ORDER BY DESC using index (unique)
# decription:   ORDER BY X
#               When a index can be used for sorting, use it.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_sort_by_index_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Table_100 (
  ID INTEGER NOT NULL
);

SET TERM ^^ ;
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
SET TERM ; ^^

COMMIT;

EXECUTE PROCEDURE PR_FillTable_100;

COMMIT;

CREATE DESC INDEX PK_Table_100_DESC ON Table_100 (ID);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
SELECT
  *
FROM
  Table_100 t100
ORDER BY
  t100.ID DESC;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (T100 ORDER PK_TABLE_100_DESC)

          ID
============

         100
          99
          98
          97
          96
          95
          94
          93
          92
          91
          90
          89
          88
          87
          86
          85
          84
          83
          82
          81

          ID
============
          80
          79
          78
          77
          76
          75
          74
          73
          72
          71
          70
          69
          68
          67
          66
          65
          64
          63
          62
          61

          ID
============
          60
          59
          58
          57
          56
          55
          54
          53
          52
          51
          50
          49
          48
          47
          46
          45
          44
          43
          42
          41

          ID
============
          40
          39
          38
          37
          36
          35
          34
          33
          32
          31
          30
          29
          28
          27
          26
          25
          24
          23
          22
          21

          ID
============
          20
          19
          18
          17
          16
          15
          14
          13
          12
          11
          10
           9
           8
           7
           6
           5
           4
           3
           2
           1
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

