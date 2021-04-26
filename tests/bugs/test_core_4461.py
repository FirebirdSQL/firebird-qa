#coding:utf-8
#
# id:           bugs.core_4461
# title:        nbackup prints error messages to stdout instead stderr
# decription:   
# tracker_id:   CORE-4461
# min_versions: ['2.5.4']
# versions:     2.5.4
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.4
# resources: None

substitutions_1 = [('Failure: Database error', '')]

init_script_1 = """
   -- NB: line `Failure: Database error` exists only in 2.5.x output.
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# runProgram('nbackup',['-user','nonExistentFoo','-pas','invalidBar','-L',dsn])
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
  [
   PROBLEM ON "attach database".
   Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
   SQLCODE:-902
  ]
  """

@pytest.mark.version('>=2.5.4')
@pytest.mark.xfail
def test_core_4461_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


