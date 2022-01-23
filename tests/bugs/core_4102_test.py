#coding:utf-8

"""
ID:          issue-4430
ISSUE:       4430
TITLE:       Bad optimization of OR predicates applied to unions
DESCRIPTION:
JIRA:        CORE-4102
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET PLANONLY;
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

act = isql_act('db', test_script)

expected_stdout = """PLAN (X R INDEX (RDB$INDEX_1, RDB$INDEX_1), X R INDEX (RDB$INDEX_1, RDB$INDEX_1))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

