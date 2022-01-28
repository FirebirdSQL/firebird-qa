#coding:utf-8

"""
ID:          optimizer.left-join-05
TITLE:       LEFT OUTER JOIN with full match, but limited in ON clause
DESCRIPTION:
  TableX LEFT OUTER JOIN TableY with full match, but TableY results limited in ON clause.
  Which should result in partial NULL results.

  This test also tests if not the ON clause is distributed to the outer context TableX.
  Also if not the extra created nodes (comparisons) from a equality node and a A # B
  node (# =, <, <=, >=, >) are distributed to the outer context.
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE Colors (
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

db = db_factory(sql_dialect=3, init=init_script)

test_script = """SET PLAN ON;
/* LEFT JOIN should return all lookups except the 0 value */
SELECT
  f.FlowerName,
  c.ColorName
FROM
  Flowers f
  LEFT JOIN Colors c ON ((c.ColorID = f.ColorID) AND
(c.ColorID >= 1));"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (F NATURAL, C INDEX (PK_COLORS))
FLOWERNAME                     COLORNAME
============================== ====================

Rose                           Red
Tulip                          Yellow
Gerbera                        <null>"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
