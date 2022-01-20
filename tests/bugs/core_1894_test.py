#coding:utf-8

"""
ID:          issue-2325
ISSUE:       2325
TITLE:       Circular dependencies between computed fields crashs the engine
DESCRIPTION:
JIRA:        CORE-1894
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t (
        n integer,
        n1 computed by (n),
        n2 computed by (n1)
    );

    recreate table t2 (
        n integer,
        c1 computed by (1),
        c2 computed by (c1)
    );

    alter table t alter n1 computed by (n2);
    commit;

    set autoddl off;
    alter table t2 drop c1;
    alter table t2 add c1 computed by (c2);
    commit;

    select * from t;
    select * from t2; -- THIS LEAD SERVER CRASH (checked on WI-T4.0.0.399)

"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -Cannot have circular dependencies with computed fields

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T2.C1
    -there are 1 dependencies

    Statement failed, SQLSTATE = 42000
    Cannot have circular dependencies with computed fields

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T2.C1
    -there are 1 dependencies
"""

@pytest.mark.version('>=3.0.2')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

