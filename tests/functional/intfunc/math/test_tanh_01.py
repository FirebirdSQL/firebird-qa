#coding:utf-8
#
# id:           functional.intfunc.math.tanh_01
# title:        test for TANH  function
# decription:   
#               TANH( <number> )
#               
#               Returns the hyperbolic tangent of a number.
#                   select tanh(x) from y;
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.tanh_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select TANH(5) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                         TANH
      =======================
0.9999092042625951"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

