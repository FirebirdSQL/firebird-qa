#coding:utf-8
#
# id:           functional.intfunc.math.trunc_01
# title:        test for TRUNC function
# decription:   TRUNC( <number> [, <number> ] )
#               
#               Returns the integral part (up to the specified scale) of a number.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.string.trunc_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select trunc(-2.8), trunc(2.8)
       from rdb$database;  -- returns -2, 2
select trunc(987.65, 1), trunc(987.65, -1)
       from rdb$database;  -- returns 987.60, 980.00"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                      TRUNC                 TRUNC
      ===================== =====================
                         -2                     2


                      TRUNC                 TRUNC
      ===================== =====================
                     987.60                980.00"""

@pytest.mark.version('>=2.1')
def test_trunc_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

