#coding:utf-8
#
# id:           bugs.core_0924
# title:        An attempt to select DB_KEY from a procedure crashes the server
# decription:   
# tracker_id:   CORE-924
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_924-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('line\\s[0-9]+,', 'line x'), ('column\\s[0-9]+', 'column y')]

init_script_1 = """CREATE TABLE T1 (ID1 INTEGER NOT NULL);
SET TERM ^;
CREATE PROCEDURE AP
returns (output1 INTEGER)
AS
BEGIN
 FOR SELECT ID1 FROM T1 INTO :output1
 DO
  BEGIN
   SUSPEND;
  END
END ^
SET TERM ;^
COMMIT;
INSERT INTO T1 VALUES (1);
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT RDB$DB_KEY from AP;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42S22
Dynamic SQL Error
-SQL error code = -206
-Column unknown
-DB_KEY
-At line 1, column 8
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

