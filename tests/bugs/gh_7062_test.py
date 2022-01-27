#coding:utf-8

"""
ID:          issue-7062
ISSUE:       7062
TITLE:       Creation of expression index does not release its statement correctly
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- case-1:
    create table test_1 (n integer);
    create table test_2 (n integer);
    create index test_1_expr on test_1 computed by ((select n from test_2));
    drop table test_1;
    commit;
    drop table test_2; -- this must NOT fail (raised "SQLSTATE = 42000 / object in use" before fix)

    -- case-2:
    create table test_a (n integer);
    create table test_b (n integer);
    insert into test_a values (0);
    commit;
    create index test_a_expr on test_a computed by (1 / 0 + (select 1 from test_b));
    drop table test_a;
    commit;
    drop table test_b; -- this must NOT fail (raised "SQLSTATE = 42000 / object in use" before fix)

"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 22012
    Expression evaluation error for index "***unknown***" on table "TEST_A"
    -arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
"""

@pytest.mark.version('>=4.0.1')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
