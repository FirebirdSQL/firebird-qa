#coding:utf-8
#
# id:           functional.intfunc.math.sin_01
# title:        test for SIN function
# decription:   
#               
#                SIN( <number> )
#               
#               
#               Returns the sine of an input number that is expressed in radians.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.sin_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select CAST(SIN(12) AS DECIMAL(18,15)) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                 CAST
=====================
   -0.536572918000435

"""

@pytest.mark.version('>=2.1')
def test_sin_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

