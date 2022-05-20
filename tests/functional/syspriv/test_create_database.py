#coding:utf-8

"""
ID:          syspriv.create-database
TITLE:       Check ability to CREATE database by non-sysdba user who is granted with necessary system privilege
DESCRIPTION:
FBTEST:      functional.syspriv.create_database
NOTES:
    [20.05.2022] pzotov
    One need to specify do_not_create=True and do_not_drop=True for db_temp, otherwise this DB will be created
    and init_script will fail to check ability of DB creation. If testing machine have localized OS then such
    attempt will raise status-vector which will have localized message:
        Statement failed, SQLSTATE = 08001
        I/O error during "CreateFile (create)" operation for file "..."
        -Error while trying to create file
        -<LOCALIZED MESSAGE HERE> // ~ "file exists"
    But we will see UnicodeDecodeError instead of full lines and/or SQLSTATE or gdscode.
    Checked on 4.0.1.2692, 5.0.0.497.
"""

import pytest
from firebird.qa import *
from firebird.driver.types import DatabaseError

substitutions = [('[ \\t]+', ' '), ('MON\\$DATABASE_NAME.*TMP4TEST.TMP', 'MON$DATABASE_NAME TMP4TEST.TMP')]
db_main = db_factory()
tmp_user = user_factory('db_main', name='tmp_syspriv_user', password='123')
tmp_role = role_factory('db_main', name='tmp_role_for_create_database')
act = python_act('db_main', substitutions = substitutions)

db_temp = db_factory(filename = 'tmp4test.tmp', do_not_create=True, do_not_drop=True)


expected_stdout_isql = """
    MON$OWNER         TMP_SYSPRIV_USER
    MON$DATABASE_NAME TMP4TEST.TMP
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_user: User, tmp_role:Role, db_temp: Database, capsys):
    init_script = \
    f"""
        set wng off;
        set bail on;
        connect '{act.db.dsn}' user '{act.db.user}' password '{act.db.password}';
        alter user {tmp_user.name} grant admin role; -- this must be specified!
        commit;
        alter role {tmp_role.name} set system privileges to CREATE_DATABASE;
        commit;
        grant default {tmp_role.name} to user {tmp_user.name};
        commit;
        create database '{db_temp.dsn}' user {tmp_user.name} password '{tmp_user.password}';
        set list on;
        select mon$owner, mon$database_name from mon$database;
        commit;
        drop database;
    """

    act.isql(switches=['-q'], input=init_script, connect_db = False, credentials = False, combine_output=True)
    act.expected_stdout = expected_stdout_isql
    assert act.clean_stdout == act.clean_expected_stdout
