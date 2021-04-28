#coding:utf-8
#
# id:           functional.procedure.create.07
# title:        CREATE PROCEDURE - try create SP with same name
# decription:   CREATE PROCEDURE - try create SP with same name
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE PROCEDURE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.procedure.create.create_procedure_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM ^;
CREATE PROCEDURE test RETURNS(id INT)AS
BEGIN
  ID=4;
  SUSPEND;
END ^
SET TERM ;^
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
CREATE PROCEDURE test RETURNS(id INT)AS
BEGIN
  ID=5;
  SUSPEND;
END ^
SET TERM ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE PROCEDURE TEST failed
-Procedure TEST already exists
"""

@pytest.mark.version('>=3.0')
def test_07_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

