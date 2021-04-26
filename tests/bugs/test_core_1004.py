#coding:utf-8
#
# id:           bugs.core_1004
# title:        context already in use (BLR error)
# decription:   
# tracker_id:   CORE-1004
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1004

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM ^;

CREATE OR ALTER PROCEDURE GET_REL_NAME (REL_ID INT) RETURNS (REL_NAME VARCHAR(32))
AS
BEGIN
  FOR SELECT R.RDB$RELATION_NAME
        FROM RDB$RELATIONS R
       WHERE R.RDB$RELATION_ID = :REL_ID
        INTO :REL_NAME
  DO
    SUSPEND;
END^

SET TERM ;^

COMMIT;

"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;

CREATE OR ALTER PROCEDURE BUG
AS
DECLARE C CURSOR FOR (
      SELECT (SELECT REL_NAME FROM GET_REL_NAME(R.RDB$RELATION_ID))
        FROM RDB$RELATIONS R
    );
DECLARE REL_NAME VARCHAR(32);
BEGIN
  OPEN C;
  WHILE (1 = 1) DO
  BEGIN
    FETCH C INTO :REL_NAME;

    IF (ROW_COUNT = 0)
    THEN LEAVE;
  END

  CLOSE C;
END^

SET TERM ;^

COMMIT;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.1')
def test_core_1004_1(act_1: Action):
    act_1.execute()

