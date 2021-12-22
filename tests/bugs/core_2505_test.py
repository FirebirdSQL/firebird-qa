#coding:utf-8
#
# id:           bugs.core_2505
# title:        Built-in trigonometric functions can produce NaN and Infinity
# decription:   
# tracker_id:   CORE-2505
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select asin(2), cot(0) from rdb$database;
select acos(2) - acos(2) from rdb$database;
select LOG10(-1) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                   ASIN                     COT
======================= =======================

               SUBTRACT
=======================

                  LOG10
=======================
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for COT must be different than zero

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for ACOS must be in the range [-1, 1]

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for LOG10 must be positive

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

