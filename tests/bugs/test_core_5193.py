#coding:utf-8
#
# id:           bugs.core_5193
# title:        Precedence problem with operator IS
# decription:   
#                     Checked on WI-V3.0.1.32518,  WI-T4.0.0.184
#                 
# tracker_id:   CORE-5193
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select not false is true is unknown as boo1 from rdb$database;
    select not false = true is not unknown as boo2  from rdb$database;
    select not unknown and not unknown is not unknown as boo3  from rdb$database;
    select not not unknown is not unknown  as boo4 from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    BOO1                            <true>
    BOO2                            <true>
    BOO3                            <null>
    BOO4                            <false>
  """

@pytest.mark.version('>=3.0.1')
def test_core_5193_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

