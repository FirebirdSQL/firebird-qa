#coding:utf-8

"""
ID:          issue-5073
ISSUE:       5073
TITLE:       Table aliasing is unnecessary required when doing UPDATE ... RETURNING RDB$ pseudo-columns
DESCRIPTION:
NOTES:
  After fix #6815 execution plan contains 'Local_Table' (FB 5.0+) for DML with RETURNING clauses:
  "When such a statement is executed, Firebird should execute the statement to completion
  and collect all requested data in a type of temporary table, once execution is complete,
  fetches are done against this temporary table"
JIRA:        CORE-4774
FBTEST:      bugs.core_4774
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t(id int, x int);
    commit;
    insert into t values(1, 100);
    commit;
    set planonly;
    insert into t(id, x) values(2, 200) returning rdb$db_key;
    delete from t where id=1 returning rdb$db_key;
    update t set x=-x where id=2 returning rdb$db_key;
    update t set x=-x where id=2 returning rdb$record_version;
"""

act = isql_act('db', test_script)

# version: 3.0

expected_stdout_1 = """
    PLAN (T NATURAL)
    PLAN (T NATURAL)
    PLAN (T NATURAL)
"""

@pytest.mark.version('>=3.0,<5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 5.0

expected_stdout_2 = """
    PLAN (T NATURAL)
    PLAN (Local_Table NATURAL)

    PLAN (T NATURAL)
    PLAN (Local_Table NATURAL)

    PLAN (T NATURAL)
    PLAN (Local_Table NATURAL)
"""

@pytest.mark.version('>=5.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

