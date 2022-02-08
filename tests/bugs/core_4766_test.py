#coding:utf-8

"""
ID:          issue-5066
ISSUE:       5066
TITLE:       AV when trying to manage users list using EXECUTE STATEMENT on behalf of
  non-sysdba user which has RDB$ADMIN role
DESCRIPTION:
NOTES:
[24.11.2021] pcisar
  On FB v4.0.0.2496 this test fails as provided script file 'core_4766.sql' raises error in
  execute block->execute statement->create/drop user:
    Statement failed, SQLSTATE = 28000
    Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    -At block line: 3, col: 9
  Variant for FB 3 works fine.
JIRA:        CORE-4766
FBTEST:      bugs.core_4766
"""

import pytest
from firebird.qa import db_factory, python_act, Action

db = db_factory()

act = python_act('db', substitutions=[('TCPv.*', 'TCP'), ('.*After line \\d+.*', ''),
                                      ('find/delete', 'delete'), ('TABLE PLG\\$.*', 'TABLE PLG')])

# version: 3.0

expected_stdout_1 = """
    Srp: BOSS_SEC_NAME                   TMP_4766_BOSS
    Srp: BOSS_SEC_PLUGIN                 Srp
    Srp: BOSS_SEC_IS_ADMIN               <true>
    Srp: Statement failed, SQLSTATE = 28000
    Srp: add record error
    Srp: -no permission for INSERT access to TABLE PLG$SRP_VIEW

    Srp: MNGR_SEC_NAME                   <null>
    Srp: MNGR_SEC_PLUGIN                 <null>
    Srp: MNGR_SEC_IS_ADMIN               <null>
    Srp: Statement failed, SQLSTATE = 28000
    Srp: delete record error
    Srp: -no permission for DELETE access to TABLE PLG$SRP_VIEW


    Leg: BOSS_SEC_NAME                   TMP_4766_BOSS
    Leg: BOSS_SEC_PLUGIN                 Legacy_UserManager
    Leg: BOSS_SEC_IS_ADMIN               <true>
    Leg: Statement failed, SQLSTATE = 28000
    Leg: add record error
    Leg: -no permission for INSERT access to TABLE PLG$VIEW_USERS

    Leg: MNGR_SEC_NAME                   <null>
    Leg: MNGR_SEC_PLUGIN                 <null>
    Leg: MNGR_SEC_IS_ADMIN               <null>

    Leg: Statement failed, SQLSTATE = 28000
    Leg: find/delete record error
    Leg: -no permission for DELETE access to TABLE PLG$VIEW_USERS

"""

@pytest.mark.version('>=3.0,<4')
def test_1(act: Action, capsys):
    sql_text = (act.files_dir / 'core_4766.sql').read_text()
    subs = {'dsn': act.db.dsn, 'user_name': act.db.user, 'user_password': act.db.password,
            'current_auth_plugin': None,}
    for current_auth_plugin in ['Srp', 'Legacy_UserManager']:
        subs['current_auth_plugin'] = current_auth_plugin
        act.reset()
        act.isql(switches=['-q'], input=sql_text % subs, combine_output=True)
        for line in act.clean_stdout.splitlines():
            if line.strip():
                print(current_auth_plugin[:3] + ': ' + line)
    #
    act.reset()
    act.expected_stdout = expected_stdout_1
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """
    Leg: BOSS_SEC_NAME                   TMP_4766_BOSS
    Leg: BOSS_SEC_PLUGIN                 Legacy_UserManager
    Leg: BOSS_SEC_IS_ADMIN               <true>

    Leg: Statement failed, SQLSTATE = 28000
    Leg: add record error
    Leg: -no permission for INSERT access to TABLE PLG$VIEW_USERS
    Leg: -Effective user is TMP_4766_BOSS

    Leg: MNGR_SEC_NAME                   <null>
    Leg: MNGR_SEC_PLUGIN                 <null>
    Leg: MNGR_SEC_IS_ADMIN               <null>

    Leg: Statement failed, SQLSTATE = 28000
    Leg: find/delete record error
    Leg: -no permission for DELETE access to TABLE PLG$VIEW_USERS
    Leg: -Effective user is TMP_4766_BOSS
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action, capsys):
    sql_text = (act.files_dir / 'core_4766.sql').read_text()
    # ::: NB :::
    # Only Legacy_UserManager is checked for FB 4.0. Srp has totally different behaviour,
    # at  least for 4.0.0.1714.
    # Sent letter to dimitr and alex, 05.01.2020 22:00.
    subs = {'dsn': act.db.dsn, 'user_name': act.db.user, 'user_password': act.db.password,
            'current_auth_plugin': None,}
    for current_auth_plugin in ['Legacy_UserManager']:
        subs['current_auth_plugin'] = current_auth_plugin
        act.reset()
        act.isql(switches=['-q'], input=sql_text % subs, combine_output=True)
        for line in act.clean_stdout.splitlines():
            if line.strip():
                print(current_auth_plugin[:3] + ': ' + line)
    #
    act.reset()
    act.expected_stdout = expected_stdout_2
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
