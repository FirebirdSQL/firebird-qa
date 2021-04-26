#coding:utf-8
#
# id:           bugs.core_6318
# title:        CAST('NOW' as TIME) raises exception
# decription:   
#                  Confirmed bug on 4.0.0.1954, 4.0.0.2000
#                  Checked on 4.0.0.2004 - works fine.
#                
# tracker_id:   CORE-6318
# min_versions: ['4.0.0']
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
    select cast('now' as time) is not null from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    <true>
  """

@pytest.mark.version('>=4.0')
def test_core_6318_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

