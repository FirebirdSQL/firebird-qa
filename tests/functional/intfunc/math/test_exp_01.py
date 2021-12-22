#coding:utf-8
#
# id:           functional.intfunc.math.exp_01
# title:        test for EXP( <number> )
# decription:   Returns the exponential e to the argument.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.exp_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
select EXP( 3) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                          EXP
      =======================
20.08553692318767"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

