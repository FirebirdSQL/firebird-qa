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
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

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

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stderr_1 = """
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified
error in switch specifications
GSEC>
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    commands = """add BADPARAM -pa PWD
add BADPARAM -pas PWD
add BADPARAM -password PWD
add BADPARAM -user USR
add BADPARAM -database DB
add BADPARAM -trusted
quit
"""
    act_1.expected_stderr = expected_stderr_1
    act_1.gsec(input=commands)
    assert act_1.clean_expected_stderr == act_1.clean_stderr


