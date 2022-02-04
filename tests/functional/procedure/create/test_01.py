#coding:utf-8

"""
ID:          procedure.create-01
TITLE:       CREATE PROCEDURE
DESCRIPTION:
FBTEST:      functional.procedure.create.01
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET TERM ^;
CREATE PROCEDURE test AS
BEGIN
  POST_EVENT 'Test';
END ^
SET TERM ;^
commit;
SHOW PROCEDURE test;"""

act = isql_act('db', test_script)

expected_stdout = """Procedure text:
=============================================================================
BEGIN
  POST_EVENT 'Test';
END
============================================================================="""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
