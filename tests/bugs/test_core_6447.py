#coding:utf-8
#
# id:           bugs.core_6447
# title:        Unexpectedly different text of message for parameterized expression starting from second run
# decription:   
#                   Previous title: "SET SQLDA_DISPLAY ON: different text of message for parameterized expression starting from second run"
#                   Confirmed bug on: 4.0.0.2267, 3.0.8.33390.
#                   Checked on 4.0.0.2269; 3.0.8.33391 -- all OK.
#                 
# tracker_id:   CORE-6447
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('^((?!sqltype|SQLSTATE|(e|E)rror|number|SQLDA).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    select 1 from rdb$database where current_connection = ? and current_transaction = ?;
    select 1 from rdb$database where current_connection = ? and current_transaction = ?;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    02: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4

    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    02: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 07002
    Dynamic SQL Error
    -SQLDA error
    -No SQLDA for input values provided

    Statement failed, SQLSTATE = 07002
    Dynamic SQL Error
    -SQLDA error
    -No SQLDA for input values provided
  """

@pytest.mark.version('>=3.0.8')
def test_core_6447_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

