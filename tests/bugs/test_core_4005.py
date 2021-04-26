#coding:utf-8
#
# id:           bugs.core_4005
# title:        wrong error message with recursive CTE
# decription:   
# tracker_id:   CORE-4005
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with recursive
    c1 as (
        select 0 as i from rdb$database
        union all
        select i + 1 from c1 where i < 1
    )
    ,c2 as (
        select i, 0 as j from c1
        union all
        select j * 10 + c1.i, c2.j + 1
        from c1 c1
        join c2 c2 on c2.j < 1
    )
    select count(i) as cnt from c2
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             6
  """

@pytest.mark.version('>=2.5.3')
def test_core_4005_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

