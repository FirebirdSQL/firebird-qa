#coding:utf-8
#
# id:           functional.intfunc.math.abs_01
# title:        New Built-in Functions, Firebird 2.1 : ABS( <number> )
# decription:   test of ABS( <number> ) function Returns the absolute value of a number.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.abs_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select ABS( -1 ) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                  ABS
=====================
1"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

