#coding:utf-8

"""
ID:          procedure.create-05
TITLE:       CREATE PROCEDURE - PSQL Stataments
DESCRIPTION:
FBTEST:      functional.procedure.create.05
"""

import pytest
from firebird.qa import *

init_script = """CREATE EXCEPTION test 'test exception';
CREATE TABLE tb(id INT, text VARCHAR(32));
commit;"""

db = db_factory(init=init_script)

test_script = """SET TERM ^;
CREATE PROCEDURE dummy (id INT) AS
BEGIN
  id=id;
END ^

CREATE PROCEDURE dummy2 (id INT) RETURNS(newID INT) AS
BEGIN
  newid=id;
END ^

CREATE PROCEDURE test
AS
DECLARE VARIABLE p1 SMALLINT;
BEGIN
/* Comments */
  p1=1+1;                           /* assigment */
  EXCEPTION test;                   /* Exception */
  EXECUTE PROCEDURE dummy(:p1);    /* Call SP   */
  EXECUTE PROCEDURE dummy2(:p1) RETURNING_VALUES :p1;
  EXECUTE PROCEDURE test;         /*recursive call */
  EXIT;
  FOR SELECT id FROM tb INTO :p1 DO BEGIN
    p1=p1+2;
  END
  INSERT INTO tb(id) VALUES(:p1);
  UPDATE tb SET text='new text' WHERE id=:p1;
  DELETE FROM tb WHERE text=:p1+1;
  SELECT id FROM tb WHERE text='ggg' INTO :p1;
  IF(p1 IS NOT NULL)THEN BEGIN
    p1=NULL;
  END
  IF(p1 IS NULL)THEN p1=2;
    ELSE BEGIN
    p1=2;
  END
  POST_EVENT 'My Event';
  POST_EVENT p1;
  WHILE(p1>30)DO BEGIN
   p1=p1-1;
  END
  BEGIN
    EXCEPTION test;
    WHEN ANY DO p1=45;
  END
END ^
SET TERM ;^
commit;
SHOW PROCEDURE test;"""

act = isql_act('db', test_script)

expected_stdout = """Procedure text:
=============================================================================
DECLARE VARIABLE p1 SMALLINT;
BEGIN
/* Comments */
  p1=1+1;                           /* assigment */
  EXCEPTION test;                   /* Exception */
  EXECUTE PROCEDURE dummy(:p1);    /* Call SP   */
  EXECUTE PROCEDURE dummy2(:p1) RETURNING_VALUES :p1;
  EXECUTE PROCEDURE test;         /*recursive call */
  EXIT;
  FOR SELECT id FROM tb INTO :p1 DO BEGIN
    p1=p1+2;
  END
  INSERT INTO tb(id) VALUES(:p1);
  UPDATE tb SET text='new text' WHERE id=:p1;
  DELETE FROM tb WHERE text=:p1+1;
  SELECT id FROM tb WHERE text='ggg' INTO :p1;
  IF(p1 IS NOT NULL)THEN BEGIN
    p1=NULL;
  END
  IF(p1 IS NULL)THEN p1=2;
    ELSE BEGIN
    p1=2;
  END
  POST_EVENT 'My Event';
  POST_EVENT p1;
  WHILE(p1>30)DO BEGIN
   p1=p1-1;
  END
  BEGIN
    EXCEPTION test;
    WHEN ANY DO p1=45;
  END
END
============================================================================="""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
