#coding:utf-8

"""
ID:          issue-3672
ISSUE:       3672
TITLE:       "BLOB not found" error after creation/altering of the invalid trigger
DESCRIPTION:
JIRA:        CORE-3305
FBTEST:      bugs.core_3305
"""

import pytest
from firebird.qa import *

db = db_factory()

# version: 3.0

test_script_1 = """
    recreate table t(v int);
    commit;
    set term ^;
    create or alter trigger t_ai for t active after insert position 0 as
    begin
        new.v = 1;
    end
    ^
    set term ;^
    commit;
    insert into t(v) values(123);
    rollback;
"""

act_1 = isql_act('db', test_script_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column
"""

@pytest.mark.version('>=3,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

# version: 4.0

test_script_2 = """
    recreate table t(v int);
    commit;
    set term ^;
    create or alter trigger t_ai for t active after insert position 0 as
    begin
        new.v = 1;
    end
    ^
    set term ;^
    commit;
    insert into t(v) values(123);
    rollback;
"""

act_2 = isql_act('db', test_script_2)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column T.V
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column T.V
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr

