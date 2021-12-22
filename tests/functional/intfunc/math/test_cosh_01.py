#coding:utf-8
#
# id:           functional.intfunc.math.cosh_01
# title:        New Built-in Functions, Firebird 2.1 : COSH( <number>)
# decription:   test of COSH
#               Returns the hyperbolic cosine of a number.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.cosh_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select COSH( 1) from rdb$database;
select COSH( 0) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                         COSH
      =======================
            1.543080634815244


                         COSH
      =======================
            1.000000000000000



"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

