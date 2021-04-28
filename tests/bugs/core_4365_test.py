#coding:utf-8
#
# id:           bugs.core_4365
# title:        Equality predicate distribution does not work for some complex queries
# decription:   
# tracker_id:   CORE-4365
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$INDEX_[0-9]+', 'RDB\\$INDEX')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select *
    from (
      select r.rdb$relation_id as id
      from rdb$relations r
        join (
          select g1.rdb$generator_id as id from rdb$generators g1
          union all
          select g2.rdb$generator_id as id from rdb$generators g2
        ) rf on rf.id = r.rdb$relation_id
        left join rdb$procedures p on p.rdb$procedure_id = rf.id
    ) x
    where id = 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (JOIN (X RF G1 INDEX (RDB$INDEX_46), X RF G2 INDEX (RDB$INDEX_46), X R INDEX (RDB$INDEX_1)), X P INDEX (RDB$INDEX_22))
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

