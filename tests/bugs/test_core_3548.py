#coding:utf-8
#
# id:           bugs.core_3548
# title:        GFIX returns an error after correctly shutting down a database
# decription:   Affected only local connections
# tracker_id:   CORE-3548
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = [('^((?!Attribute|connection).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# db_conn.close()
#  runProgram('gfix',['$(DATABASE_LOCATION)bugs.core_3548.fdb','-shut','full','-force','0','-user',user_name,'-password',user_password])
#  runProgram('gstat',['$(DATABASE_LOCATION)bugs.core_3548.fdb','-h','-user',user_name,'-password',user_password])
#  runProgram('gfix',['$(DATABASE_LOCATION)bugs.core_3548.fdb','-online','-user',user_name,'-password',user_password])
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Attributes		force write, full shutdown
  """

@pytest.mark.version('>=2.5.5')
@pytest.mark.xfail
def test_core_3548_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


