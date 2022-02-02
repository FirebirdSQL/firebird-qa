#coding:utf-8

"""
ID:          issue-4681
ISSUE:       4681
TITLE:       non-priviledged user can insert and update rdb$database
DESCRIPTION:
JIRA:        CORE-4359
FBTEST:      bugs.core_4359
"""

import pytest
from firebird.qa import *

db = db_factory()
user_boss = user_factory('db', name='boss', password='123')

test_script = """
    -- Test scenario attempts to modify (or lock record) from RDB$DATABASE
    -- both for SYSDBA and non-privileged user.
    set count on;

    insert into rdb$database(rdb$security_class) values('');
    delete from rdb$database where rdb$security_class = '';
    update rdb$database set rdb$security_class = rdb$security_class where rdb$security_class = '';
    select current_user from rdb$database with lock;

    commit;

    connect '$(DSN)' user boss password '123';

    insert into rdb$database(rdb$security_class) values('');
    delete from rdb$database where rdb$security_class = '';
    update rdb$database set rdb$security_class = rdb$security_class where rdb$security_class = '';
    select current_user from rdb$database with lock;

    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 0
    Records affected: 0
    Records affected: 0
"""

# version: 3.0

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    INSERT operation is not allowed for system table RDB$DATABASE

    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$DATABASE for update WITH LOCK

    Statement failed, SQLSTATE = 28000
    no permission for INSERT access to TABLE RDB$DATABASE

    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$DATABASE

    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$DATABASE

    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$DATABASE for update WITH LOCK
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action, user_boss: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_1
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

# version: 4.0

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    INSERT operation is not allowed for system table RDB$DATABASE

    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$DATABASE for update WITH LOCK

    Statement failed, SQLSTATE = 28000
    no permission for INSERT access to TABLE RDB$DATABASE
    -Effective user is BOSS

    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$DATABASE
    -Effective user is BOSS

    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$DATABASE
    -Effective user is BOSS

    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$DATABASE for update WITH LOCK
"""


@pytest.mark.version('>=4.0')
def test_2(act: Action, user_boss: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_2
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

