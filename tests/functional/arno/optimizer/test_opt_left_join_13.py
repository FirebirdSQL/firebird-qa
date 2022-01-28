#coding:utf-8

"""
ID:          optimizer.left-join-13
TITLE:       LEFT OUTER JOIN VIEW with full match
DESCRIPTION:
  TableX LEFT OUTER JOIN ViewY with full match. Every reference from ViewY should have a value.
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

CREATE VIEW VW_Colors (
  ColorID,
  ColorName
)
AS
SELECT
  c.ColorID,
  c.ColorName
FROM
  Colors c
;

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
/* LEFT JOIN should return all lookups */
SELECT
  f.FlowerName,
  vc.ColorName
FROM
  Flowers f
LEFT JOIN VW_Colors vc ON (vc.ColorID = f.ColorID);"""

act = isql_act('db', test_script)

expected_stdout = """PLAN JOIN (F NATURAL, VC C INDEX (PK_COLORS))
FLOWERNAME                     COLORNAME
============================== ====================

Rose                           Red
Tulip                          Yellow
Gerbera                        Not defined"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
