#coding:utf-8
#
# id:           functional.intfunc.math.acos_01
# title:        New Built-in Functions, Firebird 2.1 : ACOS( <number> )
# decription:   test of ACOS
#               
#               Returns the arc cosine of a number. Argument to ACOS must be in the range -1 to 1. Returns a value in the range 0 to PI. er.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.acos_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select cast( ACOS( 1 ) AS DECIMAL(18,15)) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                 CAST
=====================
    0.000000000000000

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

