#coding:utf-8

"""
ID:          issue-4664
ISSUE:       4664
TITLE:       Non-privileged user can delete records from RDB$SECURITY_CLASSES table
DESCRIPTION:
JIRA:        CORE-4342
"""

import pytest
from firebird.qa import *

db = db_factory()
user_boss = user_factory('db', name='boss', password='123')
user_mngr = user_factory('db', name='mngr', password='456')

test_script = """
    -- Add these DDL privileges in order to have some rows in
    -- rdb$security_classes table for user BOSS:
    grant create table to boss;
    grant alter any table to boss;
    grant drop any table to boss;
    commit;

    set list on;
    select current_user,count(*) acl_count from rdb$security_classes where rdb$acl containing 'boss';

    select 1 from rdb$security_classes where rdb$acl containing 'boss' with lock;
    update rdb$security_classes set rdb$security_class = rdb$security_class where rdb$acl containing 'boss';
    delete from rdb$security_classes where rdb$acl containing 'boss';
    commit;

    connect '$(DSN)' user 'MNGR' password '456';
    select current_user,count(*) acl_count from rdb$security_classes where rdb$acl containing 'boss';

    select 1 from rdb$security_classes where rdb$acl containing 'boss' with lock;
    update rdb$security_classes set rdb$security_class = rdb$security_class where rdb$acl containing 'boss';
    delete from rdb$security_classes where rdb$acl containing 'boss';
    commit;
"""

expected_stdout = """
    USER                            SYSDBA
    ACL_COUNT                       1

    USER                            MNGR
    ACL_COUNT                       1
"""

# version: 3.0

act = isql_act('db', test_script)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = 42000
    DELETE operation is not allowed for system table RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$SECURITY_CLASSES
"""


@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action, user_boss: User, user_mngr: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_1
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

# version: 4.0

expected_stderr_2 = """
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = 42000
    DELETE operation is not allowed for system table RDB$SECURITY_CLASSES
    Statement failed, SQLSTATE = HY000
    Cannot select system table RDB$SECURITY_CLASSES for update WITH LOCK
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to TABLE RDB$SECURITY_CLASSES
    -Effective user is MNGR
    Statement failed, SQLSTATE = 28000
    no permission for DELETE access to TABLE RDB$SECURITY_CLASSES
    -Effective user is MNGR
"""


@pytest.mark.version('>=4.0')
def test_2(act: Action, user_boss: User, user_mngr: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_2
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

