#coding:utf-8
#
# id:           bugs.core_4144
# title:        Error "context already in use (BLR error)" when preparing a query with UNION
# decription:   
# tracker_id:   CORE-4144
# min_versions: ['2.1.6']
# versions:     2.1.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set heading off;
select n
  from
  (
     select d.rdb$relation_id as n from rdb$database d
     union all
     select d.rdb$relation_id as n from rdb$database d
  )
union all
select cast(1 as bigint) from rdb$database d;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """128
128
1
"""

@pytest.mark.version('>=2.1.6')
def test_core_4144_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

