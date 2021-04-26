#coding:utf-8
#
# id:           bugs.core_1263
# title:        GSec incorrectly processes some switches
# decription:   
# tracker_id:   CORE-1263
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1263

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!invalid switch specified).)*$', ''), ('invalid switch specified.*', 'invalid switch specified'), ('.*gsec is deprecated.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# commands = """add BADPARAM -pa PWD
#  add BADPARAM -pas PWD
#  add BADPARAM -password PWD
#  add BADPARAM -user USR
#  add BADPARAM -database DB
#  add BADPARAM -trusted
#  quit
#  """
#  runProgram('gsec',['-user',user_name,'-pas',user_password],commands)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    GSEC> invalid switch specified in interactive mode
    GSEC> invalid switch specified in interactive mode
    GSEC> invalid switch specified in interactive mode
    GSEC> invalid switch specified in interactive mode
    GSEC> invalid switch specified in interactive mode
    GSEC> invalid switch specified
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_1263_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


