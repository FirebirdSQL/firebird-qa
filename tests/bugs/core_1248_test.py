#coding:utf-8
#
# id:           bugs.core_1248
# title:         Incorrect timestamp arithmetic when one of operands is negative number
# decription:   
# tracker_id:   CORE-1248
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
  set heading off;
  select cast('04.05.2007' as timestamp) - (-7) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    2007-05-11 00:00:00.0000
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

