#coding:utf-8
#
# id:           bugs.core_1550
# title:        Unnecessary index scan happens when the same index is mapped to both WHERE and ORDER BY clauses
# decription:   
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         bugs.core_1550

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(id int);
    commit;
    insert into test(id) select r.rdb$relation_id from rdb$relations r;
    commit;
    create index test_id on test(id);
    commit;

    set planonly;
    select *
    from test
    where id < 10
    order by id;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST ORDER TEST_ID)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

