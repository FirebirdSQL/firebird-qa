#coding:utf-8

"""
ID:          issue-6145-B
ISSUE:       6145
TITLE:       Allow the use of management statements in PSQL blocks
DESCRIPTION:
    Role can be set as TRUSTED when following conditions are true:
    * BOTH AuthServer and AuthClient parameters from firebird.conf contain 'Win_Sspi' as plugin, in any place;
    * current OS user has admin rights;
    * OS environment has *no* variables ISC_USER and ISC_PASSWORD (i.e. they must be UNSET);
    * Two mappings are created (both uses plugin win_sspi):
    ** from any user to user;
    ** from predefined_group domain_any_rid_admins to role <role_to_be_trusted>

    Connect to database should be done in form: CONNECT '<computername>:<our_database>' role <role_to_be_trusted>',
    and after this we can user 'SET TRUSTED ROLE' statement.

    This test checks that statement 'SET TRUSTED ROLE' can be used within PSQL block rather than as DSQL.
JIRA:        CORE-5887
FBTEST:      bugs.core_5887_trusted_role
NOTES:
    [15.08.2022] pzotov
    Checked on 5.0.0.623, 4.0.1.2692.
"""

import os
import socket
import getpass

import pytest
from firebird.qa import *

for v in ('ISC_USER','ISC_PASSWORD'):
    try:
        del os.environ[ v ]
    except KeyError as e:
        pass

THIS_COMPUTER_NAME = socket.gethostname()
CURRENT_WIN_ADMIN = getpass.getuser()

db = db_factory()
act = python_act('db', substitutions=[('\t+', ' '), ('TCPv(4|6)', 'TCP')])

tmp_role_senior = role_factory('db', name='tmp_role_5887_senior')
tmp_role_junior = role_factory('db', name='tmp_role_5887_junior')

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
def test_1(act: Action, tmp_role_junior: Role, tmp_role_senior: Role, capsys):

    sql_init = f"""
        create table test(id int);
        grant select on test to role {tmp_role_senior.name};
        commit;

        -- We have to use here "create mapping trusted_auth ... from any user to user" otherwise get
        -- Statement failed, SQLSTATE = 28000 /Missing security context for <test_database>
        -- on connect statement which specifies COMPUTERNAME:USERNAME instead path to DB:
        create or alter mapping trusted_auth using plugin win_sspi from any user to user;

        -- We have to use here "create mapping win_admins ... DOMAIN_ANY_RID_ADMINS" otherwise get
        -- Statement failed, SQLSTATE = 0P000 / Your attachment has no trusted role

        create or alter mapping win_admins1 using plugin win_sspi from predefined_group domain_any_rid_admins to role {tmp_role_junior.name};
        commit;
        create view v_info as
        select a.mon$user, a.mon$role, a.mon$remote_protocol, a.mon$auth_method from mon$attachments a where mon$attachment_id = current_connection
        ;
        grant select on v_info to public;
        commit;
    """
    act.isql(switches=['-q'], input = sql_init)
    assert act.clean_stdout == ''
    act.reset()

    sql_check = f"""
        -- This will make connection with tole = {tmp_role_junior.name}
        connect '{THIS_COMPUTER_NAME}:{act.db.db_path}';

        set list on;
        select 'point-1' as msg, v.* from v_info v;

        -- MUST FAIL because neither user nor its role has no access rights to the 'TEST' table:
        select count(*) as test_rows from test;
        commit;

        -- Make temporary connection as SYSDBA and change mapping from predefined_group domain_any_rid_admins
        -- so that any connection can get {tmp_role_senior.name} role as trusted role:
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';

        drop mapping win_admins1;
        grant {tmp_role_junior.name} to public;

        -- Following statement means that any attachment will be granted with role <tmp_role_senior>
        -- which, in turn was granted for SELECT from table 'test':
        create or alter mapping win_admins2 using plugin win_sspi from predefined_group domain_any_rid_admins to role {tmp_role_senior.name};
        commit;

        connect '{THIS_COMPUTER_NAME}:{act.db.db_path}' role {tmp_role_junior.name.upper()};

        select 'point-2' as msg, v.* from v_info v;

        set term ^;
        execute block as
        begin
            -- Following statement:
            -- 1) must pass without any error;
            -- 2) leads to change effective role from  {tmp_role_junior.name} to {tmp_role_senior.name}:
            set trusted role;
        end
        ^
        set term ;^
        commit;

        select 'point-3' as msg, v.* from v_info v;
        -- this MUST PASS because of trusted role {tmp_role_senior.name} whic has needed access rights:
        select count(*) as test_rows from test;
        commit;
    """

    expected_out = f"""
        MSG                             point-1
        MON$USER                        {THIS_COMPUTER_NAME}\\{CURRENT_WIN_ADMIN.upper()}
        MON$ROLE                        {tmp_role_junior.name.upper()}
        MON$REMOTE_PROTOCOL             TCP
        MON$AUTH_METHOD                 Mapped from Win_Sspi
        Statement failed, SQLSTATE = 28000
        no permission for SELECT access to TABLE TEST
        -Effective user is {THIS_COMPUTER_NAME}\\{CURRENT_WIN_ADMIN.upper()}

        MSG                             point-2
        MON$USER                        {THIS_COMPUTER_NAME}\\{CURRENT_WIN_ADMIN.upper()}
        MON$ROLE                        {tmp_role_junior.name.upper()}
        MON$REMOTE_PROTOCOL             TCP
        MON$AUTH_METHOD                 Mapped from Win_Sspi

        MSG                             point-3
        MON$USER                        {THIS_COMPUTER_NAME}\\{CURRENT_WIN_ADMIN.upper()}
        MON$ROLE                        {tmp_role_senior.name.upper()}
        MON$REMOTE_PROTOCOL             TCP
        MON$AUTH_METHOD                 Mapped from Win_Sspi
        TEST_ROWS                       0
    """

    act.expected_stdout = expected_out
    act.isql(switches=['-q'], input = sql_check, connect_db=False, credentials = False, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
