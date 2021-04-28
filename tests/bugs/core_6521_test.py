#coding:utf-8
#
# id:           bugs.core_6521
# title:        CAST of Infinity values to FLOAT doesn't work
# decription:   
#                   Confirmed bug on 4.0.0.2394, 3.0.8.33426
#                   Checked on intermediate builds 4.0.0.2401 (03-apr-2021 09:36), 3.0.8.33435 (03-apr-2021 09:35) -- all OK.
#                 
# tracker_id:   CORE-6521
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select cast(log(1, 1.5) as float) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Infinity
  """

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

