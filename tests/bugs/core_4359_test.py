#coding:utf-8
#
# id:           bugs.core_4359
# title:        non-priviledged user can insert and update rdb$database
# decription:
# tracker_id:   CORE-4359
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
    Records affected: 0
    Records affected: 0
"""

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

user_1_boss = user_factory('db_1', name='boss', password='123')

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action, user_1_boss: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
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

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    Records affected: 0
    Records affected: 0
    Records affected: 0
"""

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

user_2_boss = user_factory('db_2', name='boss', password='123')

@pytest.mark.version('>=4.0')
def test_2(act_2: Action, user_2_boss: User):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr
    assert act_2.clean_stdout == act_2.clean_expected_stdout

