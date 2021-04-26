#coding:utf-8
#
# id:           bugs.core_4422
# title:        FB crashes when using row_number()over( PARTITION BY x) in ORDER by clause
# decription:   
# tracker_id:   CORE-4422
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
  select 1 as n
  from rdb$database
  order by row_number()over( PARTITION BY 1);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           N
============
           1
  """

@pytest.mark.version('>=3.0')
def test_core_4422_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

