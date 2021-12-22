#coding:utf-8
#
# id:           functional.intfunc.string.reverse_01
# title:        test for REVERSE function
# decription:     REVERSE( <value> )
#               
#                Returns a string in reverse order. Useful function for creating an expression index that indexes strings from right to left.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.reverse_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select REVERSE('DRON') from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
      REVERSE
      =======
NORD"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

