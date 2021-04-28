#coding:utf-8
#
# id:           bugs.core_0852
# title:        substring(current_user from 4) fails
# decription:   select substring( current_user from 4) from rdb$database;
#               fails on string truncation
# tracker_id:   CORE-852
# min_versions: []
# versions:     2.0
# qmid:         bugs.core_852

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; 
    select substring(current_user from 4) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SUBSTRING                       DBA
  """

@pytest.mark.version('>=2.0')
def test_core_0852_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

