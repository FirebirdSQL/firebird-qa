#coding:utf-8
#
# id:           functional.procedure.create.08
# title:        CREATE PROCEDURE - COMMIT in SP is not alowed
# decription:   CREATE PROCEDURE - COMMIT in SP is not alowed
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     2.5.0
# qmid:         functional.procedure.create.create_procedure_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
CREATE PROCEDURE test RETURNS(id INT)AS
BEGIN
  COMMIT;
END ^
SET TERM ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000

Dynamic SQL Error
-SQL error code = -104
-Token unknown - line 3, column 3
-COMMIT
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

