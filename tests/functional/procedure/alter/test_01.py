#coding:utf-8
#
# id:           functional.procedure.alter.01
# title:        ALTER PROCEDURE - Simple ALTER
# decription:   ALTER PROCEDURE - Simple ALTER
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE PROCEDURE
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.procedure.alter.alter_procedure_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM ^;
CREATE PROCEDURE test RETURNS (id INTEGER)AS
BEGIN
  id=1;
END ^
SET TERM ;^
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^;
ALTER PROCEDURE test RETURNS (id INTEGER)AS
BEGIN
  id=2;
END ^
SET TERM ;^
commit;
EXECUTE PROCEDURE test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          ID
============
           2
"""

@pytest.mark.version('>=1.0')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

