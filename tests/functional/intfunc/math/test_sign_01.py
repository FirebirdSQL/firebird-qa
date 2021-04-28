#coding:utf-8
#
# id:           functional.intfunc.math.sign_01
# title:        test for SIGN function
# decription:   
#               SIGN( <number> )
#               
#                Returns 1, 0, or -1 depending on whether the input value is positive, zero or negative, respectively.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.sign_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select SIGN(-9) from rdb$database;
 select SIGN(8) from rdb$database;
 select SIGN(0) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """         SIGN
      =======
           -1


         SIGN
      =======
            1


         SIGN
      =======
            0"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

