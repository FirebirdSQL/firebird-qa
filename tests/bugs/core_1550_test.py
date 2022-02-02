#coding:utf-8

"""
ID:          issue-1967
ISSUE:       1967
TITLE:       Unnecessary index scan happens when the same index is mapped to both WHERE and ORDER BY clauses
DESCRIPTION:
JIRA:        CORE-1550
FBTEST:      bugs.core_1550
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (TEST ORDER TEST_ID)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

