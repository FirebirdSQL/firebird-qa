#coding:utf-8
#
# id:           bugs.core_3311
# title:        Error "data type unknown" while preparing UPDATE/DELETE statements with the parameterized ROWS clause
# decription:   
# tracker_id:   CORE-3311
# min_versions: ['2.5.1']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(id int);
    commit;
    insert into test select rand()*1000 from rdb$types,(select 1 i from rdb$types rows 10);
    commit;
    create index test_id on test(id);
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select * from test rows ?;
    select * from test where id between ? and ? order by id  rows ? to ?;
    update test set id=id rows ? to ?;
    update test set id=id where id between ? and ? order by id rows ? to ?;
    delete from test rows ? to ?;
    delete from test where id between ? and ? order by id  rows ? to ?;
    merge into test t 
    using( 
      select id from test where id between ? and ? rows ?
    ) s 
    on t.id=s.id 
    when matched then update set t.id=s.id;
    merge into test t 
    using( 
      select id from test where id between ? and ? order by id rows ? 
    ) s 
    on t.id=s.id 
    when matched then update set t.id=s.id;
    set planonly;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST NATURAL)
    PLAN (TEST ORDER TEST_ID)
    PLAN (TEST NATURAL)
    PLAN (TEST ORDER TEST_ID)
    PLAN (TEST NATURAL)
    PLAN (TEST ORDER TEST_ID)
    PLAN JOIN (S TEST INDEX (TEST_ID), T INDEX (TEST_ID))
    PLAN JOIN (S TEST ORDER TEST_ID, T INDEX (TEST_ID))
  """

@pytest.mark.version('>=3.0')
def test_core_3311_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

