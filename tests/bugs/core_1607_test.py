#coding:utf-8

"""
ID:          issue-2028
ISSUE:       2028
TITLE:       Correlated subquery is optimized badly if it depends on the union stream
DESCRIPTION:
JIRA:        CORE-1607
FBTEST:      bugs.core_1607
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET PLANONLY ON;
select 1
from ( select rdb$relation_name, ( select 1 from rdb$database ) as c from rdb$relations ) r
where exists ( select * from rdb$relation_fields f where f.rdb$relation_name = r.rdb$relation_name );
select 1
from (
  select * from rdb$relations
  union all
  select * from rdb$relations
) r
where exists ( select * from rdb$relation_fields f where f.rdb$relation_name = r.rdb$relation_name );
select ( select first 1 r.rdb$relation_name
         from rdb$relations r
         where r.rdb$relation_id = d.rdb$relation_id - 1 )
from (
  select * from rdb$database
  union all
  select * from rdb$database
) d;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (R RDB$DATABASE NATURAL)
PLAN (F INDEX (RDB$INDEX_4))
PLAN (R RDB$RELATIONS NATURAL)

PLAN (F INDEX (RDB$INDEX_4))
PLAN (R RDB$RELATIONS NATURAL, R RDB$RELATIONS NATURAL)

PLAN (R INDEX (RDB$INDEX_1))
PLAN (D RDB$DATABASE NATURAL, D RDB$DATABASE NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

