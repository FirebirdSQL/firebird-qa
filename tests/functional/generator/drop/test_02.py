#coding:utf-8

"""
ID:          generator.drop-02
FBTEST:      functional.generator.drop.02
TITLE:       DROP GENERATOR - in use
DESCRIPTION:
"""

import pytest
from firebird.qa import *

init_script = """CREATE GENERATOR test;
SET TERM ^;
CREATE PROCEDURE a AS
DECLARE VARIABLE id INT;
BEGIN
  id=GEN_ID(test,1);
END ^
SET TERM ;^
commit;"""

db = db_factory(init=init_script)

act = isql_act('db', "DROP GENERATOR test;")

expected_stderr = """Statement failed, SQLSTATE = 42000

unsuccessful metadata update
-cannot delete
-GENERATOR TEST
-there are 1 dependencies"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
