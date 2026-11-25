# coding:utf-8

"""
ID:          security.ddl_testing.tablespace.wgo_drop_afterrevoke
TITLE:       Transfer privilege DROP ANY TABLESPACE to another user, role
DESCRIPTION: 
"""

import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()
act = python_act('db')

expected_stdout = """
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-GRANT failed
-no DROP privilege with grant option on DDL "SQL$TABLESPACES"

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-GRANT failed
-no DROP privilege with grant option on DDL "SQL$TABLESPACES"

Statement failed, SQLSTATE = 28000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-no permission for DROP access to TABLESPACE "TS1"
-Effective user is GRANTEEUSER

Statement failed, SQLSTATE = 28000
unsuccessful metadata update
-DROP TABLESPACE TS2 failed
-no permission for DROP access to TABLESPACE "TS2"
-Effective user is USERWITHROLE2 
"""

test_user1 = user_factory('db', name='TableSPDDLUser', password='pass')
test_user2 = user_factory('db', name='UserWithRole', password='pass')
test_user3 = user_factory('db', name='GranteeUser', password='pass')
test_user4 = user_factory('db', name='UserWithRole2', password='pass')

test_role1 = role_factory('db', name='TableSPDDLRole')
test_role2 = role_factory('db', name='GranteeRole')


@pytest.mark.version('>=6.0')
def test_1(act: Action, test_user1: User, test_user2: User, test_user3: User, test_user4: User, test_role1: Role, test_role2: Role, tmpdir: Path):
    stdout = ""
    import shutil

    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    script = """
    GRANT TableSPDDLRole TO UserWithRole;
    GRANT GranteeRole TO UserWithRole2;
    commit;

    CREATE TABLESPACE TS1 FILE '%s';
    CREATE TABLESPACE TS2 FILE '%s';
    commit;

    GRANT DROP ANY TABLESPACE TO TableSPDDLUser WITH GRANT OPTION;
    GRANT DROP ANY TABLESPACE TO TableSPDDLRole WITH GRANT OPTION;
    commit;
    REVOKE GRANT OPTION FOR DROP ANY TABLESPACE FROM TableSPDDLUser;
    REVOKE GRANT OPTION FOR DROP ANY TABLESPACE FROM TableSPDDLRole;
    commit;
    """ % (ts1_file, ts2_file)
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input=script, credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'TableSPDDLUser', '-password', 'pass', '-q'],
             input="GRANT DROP ANY TABLESPACE TO GranteeUser;", credentials=False, combine_output=True)
    stdout += act.stdout
    act.reset()
    act.isql(switches=['-user', 'UserWithRole', '-password', 'pass', '-role', 'TableSPDDLRole', '-q'],
             input="GRANT DROP ANY TABLESPACE TO GranteeRole;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'GranteeUser', '-password', 'pass', '-q'],
             input="DROP TABLESPACE TS1;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'UserWithRole2', '-password', 'pass', '-role', 'GranteeRole', '-q'],
             input="DROP TABLESPACE TS2;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input="Drop tablespace ts1; Drop tablespace ts2;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.expected_stdout = expected_stdout
    act.stdout = stdout
    assert act.clean_stdout == act.clean_expected_stdout
