#coding:utf-8

"""
ID:          index.upper-bound-desc-2-segments
TITLE:       DESC 2-segment index upper bound
DESCRIPTION:
  Check if all 5 values are fetched with "equals" operator over first segment and
  "greater than or equal" operator on second segment. 2 values are bound to the upper
  segments and 1 value is bound to the lower segment.
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Table_2_10 (
  F1 INTEGER,
  F2 INTEGER
);

COMMIT;

INSERT INTO Table_2_10 (F1, F2) VALUES (1, 1);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 2);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 3);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 4);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 5);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 6);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 7);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 8);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 9);
INSERT INTO Table_2_10 (F1, F2) VALUES (1, 10);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 1);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 2);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 3);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 4);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 5);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 6);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 7);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 8);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 9);
INSERT INTO Table_2_10 (F1, F2) VALUES (2, 10);

COMMIT;

CREATE DESC INDEX I_Table_2_10_DESC ON Table_2_10 (F1, F2);

COMMIT;
"""

db = db_factory(sql_dialect=3, init=init_script)

test_script = """SET PLAN ON;
SELECT
  t.F1,
  t.F2
FROM
  Table_2_10 t
WHERE
t.F1 = 1 and t.F2 >= 6;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN (T INDEX (I_TABLE_2_10_DESC))

          F1           F2
============ ============

           1            6
           1            7
           1            8
           1            9
1           10"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
