#coding:utf-8
#
# id:           functional.arno.optimizer.opt_left_join_01
# title:        LEFT OUTER JOIN with no match at all
# decription:   TableX LEFT OUTER JOIN TableY with no match, thus result should contain all NULLs for TableY references.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.optimizer.opt_left_join_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
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
/* LEFT JOIN should return all NULLs */
SELECT
  f.FlowerName,
  c.ColorName
FROM
  Flowers f
  LEFT JOIN Colors c ON (1 = 0);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN JOIN (F NATURAL, C NATURAL)
FLOWERNAME                     COLORNAME
============================== ====================

Rose                           <null>
Tulip                          <null>
Gerbera                        <null>

"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

