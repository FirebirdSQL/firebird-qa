#coding:utf-8
#
# id:           functional.intfunc.math.maxvalue_01
# title:        test for MAXVALUE  function
# decription:    MAXVALUE( <value> [, <value> ...] )
#               
#                Returns the maximum value of a list of values.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.maxvalue_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ select maxvalue(54, 87, 10) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """          MAXVALUE
      ============
87"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

