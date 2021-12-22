#coding:utf-8
#
# id:           functional.arno.optimizer.opt_aggregate_distribution_09
# title:        Try to deliver HAVING CLAUSE conjunctions to the WHERE clause
# decription:   Comparisons which doesn't contain (anywhere hiding in the expression) aggregate-functions should be delivered to the where clause. The underlying aggregate stream could possible use it for a index and speed it up.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_aggregate_distribution_09

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
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
INSERT INTO Colors (ColorID, ColorName) VALUES (2, 'White');
INSERT INTO Colors (ColorID, ColorName) VALUES (3, 'Blue');
INSERT INTO Colors (ColorID, ColorName) VALUES (4, 'Yellow');
INSERT INTO Colors (ColorID, ColorName) VALUES (5, 'Black');
INSERT INTO Colors (ColorID, ColorName) VALUES (6, 'Purple');

/* insert some data with references */
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (1, 'Red Rose', 1);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (2, 'White Rose', 2);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (3, 'Blue Rose', 3);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (4, 'Yellow Rose', 4);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (5, 'Black Rose', 5);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (6, 'Red Tulip', 1);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (7, 'White Tulip', 2);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (8, 'Yellow Tulip', 4);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (9, 'Blue Gerbera', 3);
INSERT INTO Flowers (FlowerID, FlowerName, ColorID) VALUES (10, 'Purple Gerbera', 6);

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
SELECT
  f.ColorID,
  c.ColorName,
  Count(*)
FROM
  Flowers f
  LEFT JOIN Colors c ON (c.ColorID = f.ColorID)
GROUP BY
  f.ColorID, c.ColorName
HAVING
f.ColorID <= 4;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN SORT (JOIN (F INDEX (FK_FLOWERS_COLORS), C INDEX (PK_COLORS)))

     COLORID COLORNAME                            COUNT
============ ==================== =====================
           1 Red                                      2
           2 White                                    2
           3 Blue                                     2
           4 Yellow                                   2
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

