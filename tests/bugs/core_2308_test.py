#coding:utf-8
#
# id:           bugs.core_2308
# title:        SIMILAR TO produces random results with [x-y] expressions
# decription:   
# tracker_id:   CORE-2308
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """set term ^ ;
CREATE OR ALTER PROCEDURE PROC
RETURNS ( V INTEGER)
AS
 BEGIN
  IF ('b' SIMILAR TO ('[a-z]'))
  THEN v = 1;
  ELSE v = 2;
  SUSPEND;
END ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^ ;
EXECUTE BLOCK AS
DECLARE I INT = 1000;
DECLARE V INT;
BEGIN
  WHILE (I > 0) DO
  BEGIN
    I = I - 1;
    SELECT V FROM PROC INTO :V;

    IF (V <> 1)
    THEN V = 1/0;
  END
END ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

