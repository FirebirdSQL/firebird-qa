#coding:utf-8
#
# id:           bugs.core_1607
# title:        Correlated subquery is optimized badly if it depends on the union stream
# decription:   
# tracker_id:   CORE-1607
# min_versions: ['2.1']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLANONLY ON;
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN (R RDB$DATABASE NATURAL)
PLAN (F INDEX (RDB$INDEX_4))
PLAN (R RDB$RELATIONS NATURAL)

PLAN (F INDEX (RDB$INDEX_4))
PLAN (R RDB$RELATIONS NATURAL, R RDB$RELATIONS NATURAL)

PLAN (R INDEX (RDB$INDEX_1))
PLAN (D RDB$DATABASE NATURAL, D RDB$DATABASE NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

