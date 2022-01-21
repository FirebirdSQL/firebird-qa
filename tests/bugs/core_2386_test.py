#coding:utf-8

"""
ID:          issue-2808
ISSUE:       2808
TITLE:       ALTER VIEW could remove column used in stored procedure or trigger
DESCRIPTION:
JIRA:        CORE-2386
"""

import pytest
from firebird.qa import *

init_script = """SET TERM ^ ;

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

db = db_factory(init=init_script)

test_script = """ALTER VIEW V_TEST (F1) AS
 SELECT 1 FROM RDB$DATABASE ;"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-COLUMN V_TEST.F2
-there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

