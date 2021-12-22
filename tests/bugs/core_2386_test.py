#coding:utf-8
#
# id:           bugs.core_2386
# title:        ALTER VIEW could remove column used in stored procedure or trigger
# decription:   
# tracker_id:   CORE-2386
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM ^ ;

CREATE VIEW V_TEST (F1, F2)
AS
  SELECT 1, 2 FROM RDB$DATABASE
^

CREATE PROCEDURE SP_TEST
AS
DECLARE I INT;
BEGIN
  SELECT F1, F2 FROM V_TEST
    INTO :I, :I;
END
^

COMMIT
^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER VIEW V_TEST (F1) AS
 SELECT 1 FROM RDB$DATABASE ;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-COLUMN V_TEST.F2
-there are 1 dependencies
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

