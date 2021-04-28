#coding:utf-8
#
# id:           bugs.core_5700
# title:        DECFLOAT underflow should yield zero instead of an error
# decription:   
#                   Test case is based on letter from Alex, 05-feb-2018 20:23.
#                   Confirmed on 4.0.0.800 (15-nov-18): evaluation of '1e-5000 / 1e5000' did raise exception:
#                   ===
#                       Statement failed, SQLSTATE = 22003
#                       Decimal float underflow.  The exponent of a result is less than the magnitude allowed.
#                   ===
#                   Checked on 4.0.0.875: OK, 1.000s.
#                
# tracker_id:   CORE-5700
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         bugs.core_5700

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[\\s]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 1e-5000 / 1e5000 as r from rdb$database; -- this should NOT raise exception since this ticket was fixed.
    set decfloat traps to underflow;
    select 1e-5000 / 1e5000 as r from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    R                                                                  0E-6176
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Decimal float underflow.  The exponent of a result is less than the magnitude allowed.
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

