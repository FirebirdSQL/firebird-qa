#coding:utf-8

"""
ID:          issue-2376
ISSUE:       2376
TITLE:       Provide ability to see in the trace log actions related to session management (e.g. ALTER SESSION RESET)
DESCRIPTION:
  Test verifies management statements which are specified in doc/sql.extensions/README.management_statements_psql.md
  We launch trace session before ISQL and stop it after its finish.
  Every management statement is expected to be found in the trace log.

  ATTENTION: TWO SEPARATE BRANCHES present in this test for different OS.

  NOTES FOR WINDOWS
  #################
    Statement 'SET TRUSTED ROLE' is verified for appearance in the trace log.
    There are several prerequisites that must be met for check SET TRUSTED ROLE statement:
        * BOTH AuthServer and AuthClient parameters from firebird.conf contain 'Win_Sspi' as plugin, in any place;
        * current OS user has admin rights;
        * OS environment has *no* variables ISC_USER and ISC_PASSWORD (i.e. they must be UNSET);
        * Two mappings are created (both uses plugin win_sspi):
        ** from any user to user;
        ** from predefined_group domain_any_rid_admins to role <role_to_be_trusted>

    Connect to database should be done in form: CONNECT '<computername>:<our_database>' role <role_to_be_trusted>',
    and after this we can user 'SET TRUSTED ROLE' statement (see also: core_5887-trusted_role.fbt).

    ::: NOTE :::
    We have to remove OS-veriable 'ISC_USER' before any check of trusted role.
    This variable could be set by other .fbts which was performed before current within batch mode (i.e. when fbt_run is called from <rundaily>)

  NOTES FOR LINUX
  ###############
    Trusted role is not verified for this case.
    Weird behaviour detected when test was ran on FB 4.0.0.2377 SuperServer: if we run this test several times (e.g. in loop) then *all*
    statements related to session management can be missed in the trace - despite the fact that they *for sure* was performed successfully
    (this can be seen in ISQL log). It seems that fail somehow related to the duration of DELAY between subsequent runs: if delay more than ~30s
    then almost no fails. But if delay is small then test can fail for almost every run.
    NO such trouble in the Classic.
    The reason currently (03-mar-2021) remains unknown.
    Sent letter to Alex et al, 03-mar-2021.
NOTES:
[09.02.2022] pcisar
  Test fails on Windows as script execution fails with:
   Statement failed, SQLSTATE = 0P000
   Your attachment has no trusted role
JIRA:        CORE-6469
FBTEST:      bugs.core_6469
"""

import pytest
import re
import socket
import getpass
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_role = role_factory('db', name='TMP$R6469')

# version: 4.0 - Windows

expected_stdout_win = """
    alter session reset
    set session idle timeout 1800 second
    set statement timeout 190 second
    set bind of decfloat to double precision
    set decfloat round ceiling
    set decfloat traps to division_by_zero
    set time zone 'america/sao_paulo'
    set role tmp$r6469
    set trusted role
"""

trace_win = ['log_initfini = false',
             'log_statement_finish = true',
             'log_errors = true',
             'time_threshold = 0',
             ]

patterns_win =  [re.compile('alter session reset', re.IGNORECASE),
                 re.compile('set session idle timeout', re.IGNORECASE),
                 re.compile('set statement timeout', re.IGNORECASE),
                 re.compile('set bind of decfloat to double precision', re.IGNORECASE),
                 re.compile('set decfloat round ceiling', re.IGNORECASE),
                 re.compile('set decfloat traps to Division_by_zero', re.IGNORECASE),
                 re.compile('set time zone', re.IGNORECASE),
                 re.compile('set role', re.IGNORECASE),
                 re.compile('set trusted role', re.IGNORECASE)]

def run_script(act: Action):
    __tracebackhide__ = True
    THIS_COMPUTER_NAME = socket.gethostname()
    CURRENT_WIN_ADMIN = getpass.getuser()
    script = f"""
    set bail on;
    set list on;
    set echo on;
    grant tmp$r6469 to "{THIS_COMPUTER_NAME}\\{CURRENT_WIN_ADMIN}";
    commit;

    -- We have to use here "create mapping trusted_auth ... from any user to user" otherwise get
    -- Statement failed, SQLSTATE = 28000 /Missing security context for C:\\FBTESTING\\QA\\MISC\\C5887.FDB
    -- on connect statement which specifies COMPUTERNAME:USERNAME instead path to DB:
    create or alter mapping trusted_auth using plugin win_sspi from any user to user;

    -- We have to use here "create mapping win_admins ... DOMAIN_ANY_RID_ADMINS" otherwise get
    -- Statement failed, SQLSTATE = 0P000 / Your attachment has no trusted role
    create or alter mapping win_admins using plugin win_sspi from predefined_group domain_any_rid_admins to role tmp$r6469;
    commit;

    -- We have to GRANT ROLE, even to SYSDBA. Otherwise:
    -- Statement failed, SQLSTATE = 0P000
    -- Role TMP$R6469 is invalid or unavailable
    grant TMP$R6469 to sysdba;
    commit;
    show role;
    show grants;
    show mapping;

    set autoddl off;
    commit;

    -- Following management statements are taken from
    -- doc/sql.extensions/README.management_statements_psql.md:
    -- ########################################################
    alter session reset;
    set session idle timeout 1800 second;
    set statement timeout 190 second;
    set bind of decfloat to double precision;
    set decfloat round ceiling;
    set decfloat traps to Division_by_zero;
    set time zone 'America/Sao_Paulo';
    set role tmp$r6469;
    commit;

    connect '{THIS_COMPUTER_NAME}:{act.db.db_path}' role tmp$r6469;

    select mon$user,mon$role,mon$auth_method from mon$attachments where mon$attachment_id = current_connection;
    commit;

    set trusted role;
    commit;

    connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
    drop mapping trusted_auth;
    drop mapping win_admins;
    commit;
    """
    act.isql(switches=['-n'], input=script)

@pytest.mark.skipif(reason='FIXME: see notes')
@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
def test_1(act: Action, test_role: Role, capsys):
    with act.trace(db_events=trace_win):
        run_script(act)
    # process trace
    for line in act.trace_log:
        if line.split():
            if act.match_any(line, patterns_win):
                print(' '.join(line.split()).lower())
    # Check
    act.expected_stdout = expected_stdout_win
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0 - Linux

expected_stdout_lin = """
    alter session reset
    set session idle timeout 1800 second
    set statement timeout 190 second
    set bind of decfloat to double precision
    set decfloat round ceiling
    set decfloat traps to division_by_zero
    set time zone 'america/sao_paulo'
    set role tmp$r6469
"""

test_script_lin = """
    set bail on;
    set list on;

    -- We have to GRANT ROLE, even to SYSDBA. Otherwise:
    -- Statement failed, SQLSTATE = 0P000
    -- Role TMP$R6469 is invalid or unavailable
    grant TMP$R6469 to sysdba;
    commit;

    select current_user as who_ami, current_role as whats_my_role from rdb$database;
    set autoddl off;
    commit;

    -- Following management statements are taken from
    -- doc/sql.extensions/README.management_statements_psql.md:
    -- ########################################################
    set echo on;
    alter session reset;
    set session idle timeout 1800 second;
    set statement timeout 190 second;
    set bind of decfloat to double precision;
    set decfloat round ceiling;
    set decfloat traps to Division_by_zero;
    set time zone 'America/Sao_Paulo';
    set role tmp$r6469;
    commit;
    select 'Completed' as msg from rdb$database;
"""

trace_lin = ['log_initfini = false',
             'log_connections = true',
             'log_statement_finish = true',
             'log_errors = true',
             'time_threshold = 0',
             ]

patterns_lin =  [re.compile('alter session reset', re.IGNORECASE),
                 re.compile('set session idle timeout', re.IGNORECASE),
                 re.compile('set statement timeout', re.IGNORECASE),
                 re.compile('set bind of decfloat to double precision', re.IGNORECASE),
                 re.compile('set decfloat round ceiling', re.IGNORECASE),
                 re.compile('set decfloat traps to Division_by_zero', re.IGNORECASE),
                 re.compile('set time zone', re.IGNORECASE),
                 re.compile('set role', re.IGNORECASE)]

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Linux')
def test_2(act: Action, test_role: Role, capsys):
    with act.trace(db_events=trace_lin):
        act.isql(switches=['-n'], input=test_script_lin)
    # process trace
    for line in act.trace_log:
        if line.split():
            if act.match_any(line, patterns_lin):
                print(' '.join(line.split()).lower())
    # Check
    act.expected_stdout = expected_stdout_lin
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
