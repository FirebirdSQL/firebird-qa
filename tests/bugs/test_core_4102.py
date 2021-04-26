#coding:utf-8
#
# id:           bugs.core_4102
# title:        Bad optimization of OR predicates applied to unions
# decription:   
# tracker_id:   CORE-4102
# min_versions: ['2.5.3']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLANONLY;
select * from
(
  select rdb$relation_id as id
    from rdb$relations r
  union all
  select rdb$relation_id as id
    from rdb$relations r
) x
where x.id = 0 or x.id = 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN (X R INDEX (RDB$INDEX_1, RDB$INDEX_1), X R INDEX (RDB$INDEX_1, RDB$INDEX_1))
"""

@pytest.mark.version('>=3.0')
def test_core_4102_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

