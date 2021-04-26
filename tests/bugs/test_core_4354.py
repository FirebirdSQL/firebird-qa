#coding:utf-8
#
# id:           bugs.core_4354
# title:        Parsing of recursive query returns error "Column does not belong to referenced table" for source that HAS such column
# decription:   
# tracker_id:   CORE-4354
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='NONE', sql_dialect=3, init=init_script_1)

test_script_1 = """
with recursive
b as (
    select 0 rc
    from rdb$database qa

    union all

    select b.rc+1
    from b
        join rdb$database q1 on q1.rdb$relation_id*0=b.rc*0
        join rdb$database q2 on q2.rdb$relation_id*0=b.rc*0
    where b.rc=0
)
select * from b;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          RC
============
           0
           1
  """

@pytest.mark.version('>=3.0')
def test_core_4354_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

