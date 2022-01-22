#coding:utf-8

"""
ID:          issue-3678
ISSUE:       3678
TITLE:       Error "data type unknown" while preparing UPDATE/DELETE statements with the parameterized ROWS clause
DESCRIPTION:
JIRA:        CORE-3311
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table test(id int);
    commit;
    insert into test select rand()*1000 from rdb$types,(select 1 i from rdb$types rows 10);
    commit;
    create index test_id on test(id);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
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
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

