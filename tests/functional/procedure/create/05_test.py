#coding:utf-8
#
# id:           functional.procedure.create.05
# title:        CREATE PROCEDURE - PSQL Stataments
# decription:   CREATE PROCEDURE - PSQL Stataments
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE EXCEPTION
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.procedure.create.create_procedure_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE EXCEPTION test 'test exception';
CREATE TABLE tb(id INT, text VARCHAR(32));
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
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
=============================================================================
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

