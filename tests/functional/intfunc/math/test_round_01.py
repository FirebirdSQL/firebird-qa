#coding:utf-8
#
# id:           functional.intfunc.math.round_01
# title:        test for ROUND function
# decription:   
#               
#                ROUND( <number>, <number> )
#               
#                Returns a number rounded to the specified scale.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.round_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select ROUND(5.7778, 3) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                      ROUND
      =====================
                     5.7780"""

@pytest.mark.version('>=2.1')
def test_round_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

