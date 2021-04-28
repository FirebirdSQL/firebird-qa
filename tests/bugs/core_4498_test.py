#coding:utf-8
#
# id:           bugs.core_4498
# title:        FB 3.0 crashes when getting an explained plan for a DBKEY based retrieval
# decription:   
# tracker_id:   CORE-4498
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
  out nul;
  set explain;
  select 1 from rdb$relations where rdb$db_key = cast('1234' as char(8) character set octets); 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  Select Expression
        -> Filter
            -> Table "RDB$RELATIONS" Access By ID
                -> DBKEY
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

