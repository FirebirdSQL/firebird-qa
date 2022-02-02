#coding:utf-8

"""
ID:          issue-5414
ISSUE:       5414
TITLE:       Compiler issues message about "invalid request BLR" when attempt to compile
  wrong DDL of view with both subquery and "WITH CHECK OPTION" in its DDL
DESCRIPTION:
JIRA:        CORE-5130
FBTEST:      bugs.core_5130
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Confirmed proper result on:  WI-V3.0.0.32380
    create or alter view v1 as select 1 id from rdb$database;
    recreate table t1(id int, x int, y int);
    commit;

    alter view v1 as
    select * from t1 a
    where
        not exists(select * from t1 r where r.x > a.x)
    with check option
    ;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER VIEW V1 failed
    -Dynamic SQL Error
    -SQL error code = -607
    -No subqueries permitted for VIEW WITH CHECK OPTION
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
