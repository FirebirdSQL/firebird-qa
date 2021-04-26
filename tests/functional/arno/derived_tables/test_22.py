#coding:utf-8
#
# id:           functional.arno.derived_tables.derived_tables_22
# title:        Derived table outer reference (triggers)
# decription:   NEW/OLD context variables should be available inside the derived table.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.arno.derived_tables.derived_tables_22

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TABLEA
(
  ID INTEGER NOT NULL,
  DESCRIPTION VARCHAR(50),
  PARENTID INTEGER,
  CONSTRAINT PK_TABLEA PRIMARY KEY (ID),
  CONSTRAINT FK_TABLEA_TABLEA
    FOREIGN KEY (PARENTID) REFERENCES TABLEA (ID)
    ON DELETE NO ACTION ON UPDATE CASCADE
);

COMMIT;

SET TERM ^^ ;
CREATE TRIGGER TABLEA_BI FOR TABLEA ACTIVE BEFORE INSERT POSITION 0 AS
DECLARE PREV_ID INTEGER;
BEGIN
  PREV_ID = NULL;
  SELECT ID FROM (SELECT MAX(a.ID) AS ID FROM TABLEA a WHERE a.ID < NEW.ID) INTO :PREV_ID;
  NEW.PARENTID = PREV_ID;
END
^^
SET TERM ; ^^


SET TERM ^^ ;
CREATE TRIGGER TABLEA_BU FOR TABLEA ACTIVE BEFORE UPDATE POSITION 0 AS
DECLARE PREV_ID INTEGER;
BEGIN
  PREV_ID = NULL;
  SELECT ID FROM (SELECT MAX(a.ID) AS ID FROM TABLEA a WHERE a.ID < OLD.ID) INTO :PREV_ID;
  SELECT ID FROM (SELECT MAX(a.ID) AS ID FROM TABLEA a WHERE a.ID < NEW.ID) INTO :PREV_ID;
  NEW.PARENTID = PREV_ID;
END
^^
SET TERM ; ^^


SET TERM ^^ ;
CREATE TRIGGER TABLEA_BD FOR TABLEA ACTIVE BEFORE DELETE POSITION 0 AS
DECLARE PREV_ID INTEGER;
BEGIN
  PREV_ID = NULL;
  SELECT ID FROM (SELECT MAX(a.ID) AS ID FROM TABLEA a WHERE a.ID < OLD.ID) INTO :PREV_ID;
END
^^
SET TERM ; ^^

COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """INSERT INTO TABLEA (ID, DESCRIPTION) VALUES (1, 'Blue');
INSERT INTO TABLEA (ID, DESCRIPTION) VALUES (2, 'Red');
INSERT INTO TABLEA (ID, DESCRIPTION) VALUES (4, 'Green');
INSERT INTO TABLEA (ID, DESCRIPTION) VALUES (8, 'Yellow');
COMMIT;
SELECT * FROM TABLEA;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          ID DESCRIPTION                                            PARENTID
============ ================================================== ============
           1 Blue                                                     <null>
           2 Red                                                           1
           4 Green                                                         2
           8 Yellow                                                        4"""

@pytest.mark.version('>=2.0')
def test_derived_tables_22_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

