#coding:utf-8
#
# id:           bugs.core_2765
# title:        Use of RDB$ADMIN role does not provide SYSDBA rights in GRANT/REVOKE
# decription:
#                   06.08.2018: removed old code for 3.0 and 4.0, replaced it with simplified one that does *exactly* what ticket says.
#                   Checked on 3.0.4.33021, 4.0.0.1143.
#
# tracker_id:   CORE-2765
# min_versions: ['2.5.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = [('no (S|SELECT) privilege with grant option on table/view TEST', 'no SELECT privilege with grant option on table/view TEST')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    --set bail on;
    set list on;
    set wng off;

    grant rdb$admin to tmp$c2765_admin;
    commit;

    recreate table test(id int, x int);
    commit;
    insert into test(id, x) values(1, 1000);
    commit;

    connect '$(DSN)' user tmp$c2765_admin password '123' role 'RDB$ADMIN';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;
    --select * from test;
    commit;

    grant all on test to tmp$c2765_worker1;
    commit;

    connect '$(DSN)' user tmp$c2765_worker1 password '456';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;

    -- all these statements should pass:
    set count on;
    select * from test;
    update test set id=-id;
    delete from test;
    insert into test(id,x) values(2, 2000);
    set count off;
    rollback;


    connect '$(DSN)' user tmp$c2765_admin password '123';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;
    commit;

    grant all on test to tmp$c2765_worker2; -- should fail!
    commit;

    connect '$(DSN)' user tmp$c2765_worker2 password '789';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;
    select * from test; -- should FAIL!
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP$C2765_ADMIN
    WHAT_IS_MY_ROLE                 RDB$ADMIN

    WHO_AM_I                        TMP$C2765_WORKER1
    WHAT_IS_MY_ROLE                 NONE
    ID                              1
    X                               1000

    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1

    WHO_AM_I                        TMP$C2765_ADMIN
    WHAT_IS_MY_ROLE                 NONE

    WHO_AM_I                        TMP$C2765_WORKER2
    WHAT_IS_MY_ROLE                 NONE

"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -no SELECT privilege with grant option on table/view TEST
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
"""

user_1_admin = user_factory('db_1', name='tmp$c2765_admin', password='123')
user_1_work1 = user_factory('db_1', name='tmp$c2765_worker1', password='456')
user_1_work2 = user_factory('db_1', name='tmp$c2765_worker2', password='789')

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action, user_1_admin: User, user_1_work1: User, user_1_work2: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = [('no (S|SELECT) privilege with grant option on table/view TEST', 'no SELECT privilege with grant option on table/view TEST')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    --set bail on;
    set list on;
    set wng off;

    grant rdb$admin to tmp$c2765_admin;
    commit;

    recreate table test(id int, x int);
    commit;
    insert into test(id, x) values(1, 1000);
    commit;

    connect '$(DSN)' user tmp$c2765_admin password '123' role 'RDB$ADMIN';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;
    --select * from test;
    commit;

    grant all on test to tmp$c2765_worker1;
    commit;

    connect '$(DSN)' user tmp$c2765_worker1 password '456';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;

    -- all these statements should pass:
    set count on;
    select * from test;
    update test set id=-id;
    delete from test;
    insert into test(id,x) values(2, 2000);
    set count off;
    rollback;


    connect '$(DSN)' user tmp$c2765_admin password '123';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;
    commit;

    grant all on test to tmp$c2765_worker2; -- should fail!
    commit;

    connect '$(DSN)' user tmp$c2765_worker2 password '789';
    select current_user as who_am_i, current_role as what_is_my_role from rdb$database;
    select * from test; -- should FAIL!
    commit;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    WHO_AM_I                        TMP$C2765_ADMIN
    WHAT_IS_MY_ROLE                 RDB$ADMIN

    WHO_AM_I                        TMP$C2765_WORKER1
    WHAT_IS_MY_ROLE                 NONE
    ID                              1
    X                               1000

    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1

    WHO_AM_I                        TMP$C2765_ADMIN
    WHAT_IS_MY_ROLE                 NONE

    WHO_AM_I                        TMP$C2765_WORKER2
    WHAT_IS_MY_ROLE                 NONE

"""

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -no SELECT privilege with grant option on table/view TEST
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP$C2765_WORKER2
"""

user_2_admin = user_factory('db_2', name='tmp$c2765_admin', password='123')
user_2_work1 = user_factory('db_2', name='tmp$c2765_worker1', password='456')
user_2_work2 = user_factory('db_2', name='tmp$c2765_worker2', password='789')

@pytest.mark.version('>=4.0')
def test_2(act_2: Action, user_2_admin: User, user_2_work1: User, user_2_work2: User):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr
    assert act_2.clean_stdout == act_2.clean_expected_stdout

