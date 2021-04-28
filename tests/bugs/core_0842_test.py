#coding:utf-8
#
# id:           bugs.core_0842
# title:        Specific query crashing server
# decription:   Run the query below twice and the server will crash:
#               
#               select
#                  cast('' as varchar(32765)),
#                  cast('' as varchar(32748))
#               from
#                  rdb$database;
# tracker_id:   CORE-842
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_842

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
  set list on;
  select cast('' as varchar(32765)), cast('' as varchar(32748)) from rdb$database;
  select cast('' as varchar(32765)), cast('' as varchar(32748)) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CAST
    CAST
    CAST
    CAST
 """

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

