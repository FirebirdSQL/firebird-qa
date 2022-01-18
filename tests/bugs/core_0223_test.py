#coding:utf-8

"""
ID:          issue-554
ISSUE:       554
TITLE:       ALTER TABLE altering to VARCHAR
DESCRIPTION:
JIRA:        CORE-223
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table test1(x int);
    --create index test1_x on test1(x);

    insert into test1 values(2000000000);
    insert into test1 values(100000000);
    insert into test1 values(50000000);
    commit;

    select * from test1 order by x;
    commit;

    alter table test1 alter x type varchar(5);
    alter table test1 alter x type varchar(9);

    alter table test1 alter x type varchar(11);

    -- Here values must be sorted as TEXT:
    select * from test1 order by x;
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    X                               50000000
    X                               100000000
    X                               2000000000

    X                               100000000
    X                               2000000000
    X                               50000000
"""
expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -New size specified for column X must be at least 11 characters.

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST1 failed
    -New size specified for column X must be at least 11 characters.
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

