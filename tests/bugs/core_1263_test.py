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

expected_stderr_1_a = """
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified
error in switch specifications
GSEC>
"""

commands_1 = """add BADPARAM -pa PWD
add BADPARAM -pas PWD
add BADPARAM -password PWD
add BADPARAM -user USR
add BADPARAM -database DB
add BADPARAM -trusted
quit
"""

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Linux', 'Darwin')
def test_1_a(act_1: Action):
    act_1.expected_stderr = expected_stderr_1_a
    act_1.gsec(input=commands_1)
    assert act_1.clean_stderr == act_1.clean_expected_stderr

expected_stderr_1_b = """
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC> invalid switch specified in interactive mode
GSEC>
"""

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Windows')
def test_1_b(act_1: Action):
    act_1.expected_stderr = expected_stderr_1_b
    act_1.gsec(input=commands_1)
    assert act_1.clean_stderr == act_1.clean_expected_stderr



