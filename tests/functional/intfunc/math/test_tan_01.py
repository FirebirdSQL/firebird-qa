#coding:utf-8
#
# id:           functional.intfunc.math.tan_01
# title:        test for TAN  function
# decription:   
#                TAN( <number> )
#               
#               Returns the tangent of an input number that is expressed in radians.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.tan_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select TAN(43) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                          TAN
      =======================
           -1.498387338855171"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

