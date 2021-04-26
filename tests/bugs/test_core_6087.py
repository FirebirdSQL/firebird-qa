#coding:utf-8
#
# id:           bugs.core_6087
# title:        Problem with casting within UNION
# decription:   
#                   Confirmed bug on WI-T4.0.0.1533.
#                   Checked on 4.0.0.1534: OK, 1.465s.
#                
# tracker_id:   CORE-6087
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
   set list on;
   select cast(0.1234 as int) as result from rdb$database
   union all
   select cast(0.1234 as numeric(18,4)) from rdb$database
   ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          0.0000
    RESULT                          0.1234
  """

@pytest.mark.version('>=4.0')
def test_core_6087_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

