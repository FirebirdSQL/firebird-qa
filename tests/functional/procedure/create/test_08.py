#coding:utf-8

"""
ID:          procedure.create-08
TITLE:       CREATE PROCEDURE - COMMIT in SP is not alowed
DESCRIPTION:
FBTEST:      functional.procedure.create.08
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET TERM ^;
CREATE PROCEDURE test RETURNS(id INT)AS
BEGIN
  COMMIT;
END ^
SET TERM ;^"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000

Dynamic SQL Error
-SQL error code = -104
-Token unknown - line 3, column 3
-COMMIT"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
