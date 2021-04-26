#coding:utf-8
#
# id:           bugs.core_2822
# title:        Error "no current row for fetch operation" when subquery includes a non-trivial derived table
# decription:   
# tracker_id:   CORE-2822
# min_versions: []
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select *
from rdb$relations r natural join rdb$relation_fields rf
where 1 = (
  select 1
  from (
    select 1 from rdb$database
    union
    select 1
    from rdb$fields f
    where f.rdb$field_name = rf.rdb$field_source
  ) as f (id) ) ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.4')
def test_core_2822_1(act_1: Action):
    act_1.execute()

