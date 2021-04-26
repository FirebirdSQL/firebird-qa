#coding:utf-8
#
# id:           functional.procedure.create.01
# title:        CREATE PROCEDURE
# decription:   CREATE PROCEDURE
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.procedure.create.create_procedure_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
CREATE PROCEDURE test AS
BEGIN
  POST_EVENT 'Test';
END ^
SET TERM ;^
commit;
SHOW PROCEDURE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
=============================================================================
BEGIN
  POST_EVENT 'Test';
END
=============================================================================
"""

@pytest.mark.version('>=2.1')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

