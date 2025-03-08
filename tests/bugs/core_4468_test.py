#coding:utf-8

"""
ID:          issue-4788
ISSUE:       4788
TITLE:       FB3: CREATE USER GRANT ADMIN ROLE does not work
DESCRIPTION:
JIRA:        CORE-4468
NOTES:
    [08.03.2025] pzotov
    1. Commented out (and will be deleted later) code that expected error when user who was granted role
       with admin option tries to revoke this role from himself. Seince fixed GH-8462 this is NOT so.
    2. Replaced hard-coded names/passwords with variables that are provided by fixtures (tmp_senior, tmp_junior).

    Checked on 6.0.0.660; 5.0.3.1624; 4.0.6.3189; 3.0.13.33798
"""
import locale

import pytest
from firebird.qa import *

substitutions = [('.*delete record.*', 'delete record'),
                 ('TABLE PLG\\$VIEW_USERS', 'TABLE PLG'),
                 ('TABLE PLG\\$SRP_VIEW', 'TABLE PLG'),
                 ('-Effective user is.*', '')]

db = db_factory()

tmp_senior = user_factory('db', name='ozzy_osbourne', password='123', admin=True)
tmp_junior = user_factory('db', name='bon_scott', password='456')

act = isql_act('db', substitutions=substitutions)

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_senior: User, tmp_junior: User):

    test_sql = f"""
        set wng off;
        set list on;
        set count on;

        -- ::: NB ::: Name of PLG-* depends on value of UserManager = Srp or Legacy_UserManager.
        -- For 'Srp' it will be 'PLG$SRP_VIEW', for Legacy_UserManager -- PLG$VIEW_USERS.
        -- Because of this, section 'substitution' has been added in order to ignore rest part of line
        -- after words 'TABLE PLG'.
        -- Also, text in message about deletion fault differs in case of UserManager setting:
        -- 'find/delete record error' - for Legacy_UserManager
        -- 'delete record error' = for Srp
        -- This is minor bug in Legacy_UserManager but it will be remain 'as is', see letter from Alex 03-jun-2015 19:51.
        recreate view v_users as
        select current_user who_am_i, current_role whats_my_role, u.sec$user_name non_sysdba_user_name, u.sec$admin non_sysdba_has_admin_role
        from rdb$database
        left join sec$users u on u.sec$user_name in ( upper('{tmp_senior.name}'), upper('{tmp_junior.name}') );
        commit;
        grant select on v_users to public;
        commit;

        select 'start' msg, v.* from v_users v;
        commit;

        revoke all on all from {tmp_senior.name};
        grant rdb$admin to {tmp_senior.name}; -- this is also mandatory: it gives him admin role in ($dsn) database
        commit;

        select 'point-1' msg, v.* from v_users v;
        commit;

        -- When '{tmp_senior.name}' connects to database ($dsn), there is no way for engine to recognize that this user
        -- has been granted with admin role in 'CREATE USER ... GRANT ADMIN ROLE' statement. So, user has to specify
        -- `role 'RDB$ADMIN'` in order to connect as ADMIN.
        -- But with RDB$ADMIN only he can create objects in THAT database (tables etc), but not other USERS!
        -- Thats why he should also be granted with admin role in 'CREATE USER ...' - see above.
        connect '{act.db.dsn}' user '{tmp_senior.name}' password '{tmp_senior.password}' role 'RDB$ADMIN';
        commit;

        -- Users are stored in Security DB,  *not* in "this" database!
        -- So, following statement will pass only if '{tmp_senior.name}' has been granted by 'admin role'
        -- in his own 'create user' phase:
        create or alter user {tmp_junior.name} password '{tmp_junior.password}' revoke admin role;
        commit;

        select 'point-2' msg, v.* from v_users v;

        alter user {tmp_junior.name} grant admin role;
        commit;
        show grants;

        select 'point-3' msg, v.* from v_users v;

        grant rdb$admin to {tmp_junior.name};
        commit;

        show grants;

        alter user {tmp_junior.name} revoke admin role;
        commit;

        select 'point-4' msg, v.* from v_users v;
        commit;

        revoke rdb$admin from {tmp_junior.name};
        commit;
        show grants;

        select 'point-5' msg, v.* from v_users v;
        commit;

        -- User removes admin role from himself:

        /****************************************
        -- 1. This will FAIL:
        -- -REVOKE failed
        -- -{tmp_senior.name} is not grantor of Role on RDB$ADMIN to {tmp_senior.name}.
        revoke rdb$admin from {tmp_senior.name};
        commit;
        *******************************************/

        -- 2 This will PASS, and it MUST be so (see letter from Alex, 03-jun-2015 19:46)
        alter user {tmp_senior.name} revoke admin role;
        commit;

        show grants;

        select 'point-6' msg, v.* from v_users v;
        commit;

        -- And after previous action he can not drop himself because now he is NOT member of admin role:
        -- Statement failed, SQLSTATE = 28000
        -- find/delete record error
        -- -no permission for DELETE access to TABLE PLG$VIEW_USERS
        drop user {tmp_senior.name};
        commit;

        select 'point-7' msg, v.* from v_users v;
        commit;

        -- Trying reconnect with role RDB$ADMIN:
        connect '{act.db.dsn}' user '{tmp_senior.name}' password '{tmp_senior.password}' role 'RDB$ADMIN';
        commit;

        select 'point-8' msg, v.* from v_users v;
        commit;

        show grants;
        commit;
    """

    act.expected_stdout = """
        MSG                             start
        WHO_AM_I                        SYSDBA
        WHATS_MY_ROLE                   NONE
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        MSG                             start
        WHO_AM_I                        SYSDBA
        WHATS_MY_ROLE                   NONE
        NON_SYSDBA_USER_NAME            BON_SCOTT
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 2
        MSG                             point-1
        WHO_AM_I                        SYSDBA
        WHATS_MY_ROLE                   NONE
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        MSG                             point-1
        WHO_AM_I                        SYSDBA
        WHATS_MY_ROLE                   NONE
        NON_SYSDBA_USER_NAME            BON_SCOTT
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 2
        MSG                             point-2
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        MSG                             point-2
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            BON_SCOTT
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 2
        /* Grant permissions for this database */
        GRANT SELECT ON V_USERS TO PUBLIC
        GRANT RDB$ADMIN TO OZZY_OSBOURNE
        MSG                             point-3
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        MSG                             point-3
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            BON_SCOTT
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        Records affected: 2
        /* Grant permissions for this database */
        GRANT SELECT ON V_USERS TO PUBLIC
        GRANT RDB$ADMIN TO BON_SCOTT GRANTED BY OZZY_OSBOURNE
        GRANT RDB$ADMIN TO OZZY_OSBOURNE
        MSG                             point-4
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        MSG                             point-4
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            BON_SCOTT
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 2
        /* Grant permissions for this database */
        GRANT SELECT ON V_USERS TO PUBLIC
        GRANT RDB$ADMIN TO OZZY_OSBOURNE
        MSG                             point-5
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <true>
        MSG                             point-5
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            BON_SCOTT
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 2
        /* Grant permissions for this database */
        GRANT SELECT ON V_USERS TO PUBLIC
        GRANT RDB$ADMIN TO OZZY_OSBOURNE
        MSG                             point-6
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 1
        Statement failed, SQLSTATE = 28000
        delete record
        -no permission for DELETE access to TABLE PLG
        MSG                             point-7
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 1
        MSG                             point-8
        WHO_AM_I                        OZZY_OSBOURNE
        WHATS_MY_ROLE                   RDB$ADMIN
        NON_SYSDBA_USER_NAME            OZZY_OSBOURNE
        NON_SYSDBA_HAS_ADMIN_ROLE       <false>
        Records affected: 1
        /* Grant permissions for this database */
        GRANT SELECT ON V_USERS TO PUBLIC
        GRANT RDB$ADMIN TO OZZY_OSBOURNE
    """

    act.isql(switches = ['-q'], input = test_sql, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
