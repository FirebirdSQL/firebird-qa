#coding:utf-8
#
# id:           bugs.core_5713
# title:        Field alias disapears in complex query
# decription:   
#                   Checked on:
#                       3.0.3.32882: OK, 1.328s.
#                       4.0.0.855: OK, 1.625s.
#                
# tracker_id:   CORE-5713
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select a1, a2
    from (
      select 1 a1, 2 a2
      from rdb$database
    )
    group by 1, 2

    union all

    select 1 a1, coalesce(cast(null as varchar(64)), 0) a2
    from rdb$database;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A1                              1
    A2                              2

    A1                              1
    A2                              0
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

