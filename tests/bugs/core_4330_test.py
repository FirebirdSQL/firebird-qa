#coding:utf-8
#
# id:           bugs.core_4330
# title:        not correct result function LAG, if OFFSET value are assigned from a table
# decription:   
# tracker_id:   CORE-4330
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
    set list on;
    with t(a, b) as
    (
      select 1, null from rdb$database
      union all
      select 2, 1 from rdb$database
      union all
      select 3, 2 from rdb$database
      union all
      select 4, 3 from rdb$database
      union all
      select 5, 2 from rdb$database
    )
    select
      a,
      b,
      lag(a, b)over(order by a) as la
    from t ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               1
    B                               <null>
    LA                              <null>

    A                               2
    B                               1
    LA                              1

    A                               3
    B                               2
    LA                              1

    A                               4
    B                               3
    LA                              1

    A                               5
    B                               2
    LA                              3
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

