#coding:utf-8

"""
ID:          procedure.alter-02
TITLE:       ALTER PROCEDURE - Alter non exists procedure
DESCRIPTION:
FBTEST:      functional.procedure.alter.02
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET TERM ^;
ALTER PROCEDURE test RETURNS (id INTEGER)AS
BEGIN
  id=2;
END ^
SET TERM ;^"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER PROCEDURE TEST failed
-Procedure TEST not found"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
