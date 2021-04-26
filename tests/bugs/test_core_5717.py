#coding:utf-8
#
# id:           bugs.core_5717
# title:        Reject non-constant date/time/timestamp literals
# decription:   
#                   Checked on 4.0.0.1479: OK, 1.631s.
#                
# tracker_id:   CORE-5717
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select date '2018-01-01' from rdb$database;
    select time '10:00:00' from rdb$database;
    select timestamp '2018-01-01 10:00:00' from rdb$database;
    select DATE 'TODAY' from rdb$database;
    select DATE 'TOMORROW' from rdb$database;
    select DATE 'YESTERDAY' from rdb$database;
    select TIME 'NOW' from rdb$database;
    select TIMESTAMP 'NOW' from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    2018-01-01  
    10:00:00.0000 
    2018-01-01 10:00:00.0000  
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "TODAY"

    Statement failed, SQLSTATE = 22018
    conversion error from string "TOMORROW"

    Statement failed, SQLSTATE = 22018
    conversion error from string "YESTERDAY"

    Statement failed, SQLSTATE = 22018
    conversion error from string "NOW"

    Statement failed, SQLSTATE = 22018
    conversion error from string "NOW"
  """

@pytest.mark.version('>=4.0')
def test_core_5717_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

