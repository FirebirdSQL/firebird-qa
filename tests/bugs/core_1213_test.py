#coding:utf-8
#
# id:           bugs.core_1213
# title:        CURRENT OF support views
# decription:   
# tracker_id:   CORE-1213
# min_versions: []
# versions:     2.1.0
# qmid:         bugs.core_1213

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TAB1 (COL1 INTEGER);
CREATE VIEW V1 (COL1) AS SELECT COL1 FROM TAB1;
COMMIT;
INSERT INTO TAB1 (COL1) VALUES (1);
INSERT INTO TAB1 (COL1) VALUES (2);
INSERT INTO TAB1 (COL1) VALUES (3);
COMMIT;
SET TERM ^ ;
CREATE PROCEDURE P1 AS
DECLARE vCOL1 INTEGER;
BEGIN
FOR SELECT COL1 FROM V1 WHERE COL1 IN (2,3) INTO :vCOL1 AS CURSOR VIEW_CURSOR DO
  BEGIN
   DELETE FROM V1 WHERE CURRENT OF VIEW_CURSOR;
  END
END ^
COMMIT ^


"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT COL1 FROM V1;
EXECUTE PROCEDURE P1;
SELECT COL1 FROM V1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
        COL1
============
           1
           2
           3


        COL1
============
           1

"""

@pytest.mark.version('>=2.1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

