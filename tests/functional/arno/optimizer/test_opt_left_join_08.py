#coding:utf-8
#
# id:           functional.arno.optimizer.opt_left_join_08
# title:        LEFT OUTER JOIN with full match, but limited in ON and WHERE clause
# decription:   TableX LEFT OUTER JOIN TableY with full match, but TableY results limited in ON clause. Which should result in partial NULL results for TableY. Due the WHERE clause a index for TableX should be used.
# tracker_id:   
# min_versions: []
# versions:     2.5
# qmid:         functional.arno.optimizer.opt_left_join_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE Colors (
  ColorID INTEGER NOT NULL,
  ColorName VARCHAR(20)
);

CREATE TABLE Flowers (
  FlowerID INTEGER NOT NULL,
  FlowerName VARCHAR(30),
  ColorID INTEGER
);

COMMIT;

/* Value 0 represents -no value- */
INSERT INTO Colors (ColorID, ColorName) VALUES (0, 'Not defined');
INSERT INTO Colors (ColorID, ColorName) VALUES (1, 'Red');
INSERT INTO Colors (ColorID, ColorName) VALUES (2, 'Yellow');

/* insert some data with references */
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (1, 'Rose', 1);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (2, 'Tulip', 2);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (3, 'Gerbera', 0);

COMMIT;

/* Normally these indexes are created by the primary/foreign keys,
   but we don't want to rely on them for this test */
CREATE UNIQUE ASC INDEX PK_Colors ON Colors (ColorID);
CREATE UNIQUE ASC INDEX PK_Flowers ON Flowers (FlowerID);
CREATE ASC INDEX FK_Flowers_Colors ON Flowers (ColorID);

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
/*  */
SELECT
  f.ColorID,
  c.ColorID
FROM
  Flowers f
  LEFT JOIN Colors c ON (c.ColorID = f.ColorID) AND
    (c.ColorID > 0)
WHERE
  f.ColorID >= 0;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN JOIN (F INDEX (FK_FLOWERS_COLORS), C INDEX (PK_COLORS))

     COLORID      COLORID
============ ============
           1            1
           2            2
           0       <null>

"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

