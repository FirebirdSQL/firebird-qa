#coding:utf-8

"""
ID:          optimizer.left-join-10
TITLE:       LEFT OUTER JOIN with IS NULL burried in WHERE clause
DESCRIPTION:
  TableX LEFT OUTER JOIN TableY with no match, thus result should contain all NULLs for TableY
  references. WHERE clause contains IS NULL on a field which is also in a single segment index.
  The WHERE clause shouldn't be distributed to the joined table.
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

db = db_factory(init=init_script)

test_script = """SET PLAN ON;
/* LEFT JOIN should return all NULLs */
SELECT
  f.FlowerName,
  c.ColorName
FROM
  Flowers f
  LEFT JOIN Colors c ON (1 = 0)
WHERE
c.ColorID IS NULL or c.ColorID = 1;"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (F NATURAL, C NATURAL)
FLOWERNAME                     COLORNAME
============================== ====================

Rose                           <null>
Tulip                          <null>
Gerbera                        <null>"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
