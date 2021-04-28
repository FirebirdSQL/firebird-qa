#coding:utf-8
#
# id:           functional.intfunc.math.cot_01
# title:        test de la fonction cot
# decription:   returns 1 / tan(argument)
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.math.cot_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select cast(COT(1) AS DECIMAL(18,15)) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                 CAST
=====================
    0.642092615934331

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

