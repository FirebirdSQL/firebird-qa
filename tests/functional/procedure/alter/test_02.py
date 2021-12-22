#coding:utf-8
#
# id:           functional.procedure.alter.02
# title:        ALTER PROCEDURE - Alter non exists procedure
# decription:   ALTER PROCEDURE - Alter non exists procedure
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.procedure.alter.alter_procedure_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
ALTER PROCEDURE test RETURNS (id INTEGER)AS
BEGIN
  id=2;
END ^
SET TERM ;^"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER PROCEDURE TEST failed
-Procedure TEST not found"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

