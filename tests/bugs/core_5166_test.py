#coding:utf-8

"""
ID:          issue-5449
ISSUE:       5449
TITLE:       Wrong error message with UNIQUE BOOLEAN field
DESCRIPTION:
JIRA:        CORE-5166
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Confirmed: result is OK, builds: 3.0.0.32418, WI-T4.0.0.98
    set list on;
    recreate table test1 (
        x boolean,
        constraint test1_x_unq unique (x)
        using index test1_x_unq
    );
    commit;
    insert into test1(x) values (true);
    select * from test1;

    set count on;
    insert into test1(x) values (true);
    commit;
    set count off;

    recreate table test2 (
        u boolean,
        v boolean,
        w boolean,
        constraint test2_uvw_unq unique (u,v,w)
        using index test2_uvw_unq
    );
    commit;

    set count on;
    insert into test2 values( null, null, null);
    insert into test2 values( true, true, true);
    insert into test2 values( true, null, true);
    insert into test2 values( true, null, null);
    insert into test2 values( null, true, null);
    insert into test2 values( null, null, null);
    insert into test2 values( true, true, true);
    update test2 set u=true, v=null, w=true where coalesce(u,v,w) is null rows 1;
"""

act = isql_act('db', test_script)

expected_stdout = """
    X                               <true>
    Records affected: 0
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 0
    Records affected: 0
"""

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST1_X_UNQ" on table "TEST1"
    -Problematic key value is ("X" = TRUE)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST2_UVW_UNQ" on table "TEST2"
    -Problematic key value is ("U" = TRUE, "V" = TRUE, "W" = TRUE)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST2_UVW_UNQ" on table "TEST2"
    -Problematic key value is ("U" = TRUE, "V" = NULL, "W" = TRUE)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

