# coding:utf-8

"""
ID:          security.ddl_testing.tablespace.wgo_alter_aftergrant
TITLE:       Transfer privilege ALTER ANY TABLESPACE to another user, role
DESCRIPTION: 
"""

import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()
act = python_act('db')

expected_stdout = """
"""

test_user1 = user_factory('db', name='TableSPDDLUser', password='pass')
test_user2 = user_factory('db', name='UserWithRole', password='pass')
test_user3 = user_factory('db', name='GranteeUser', password='pass')
test_user4 = user_factory('db', name='UserWithRole2', password='pass')
test_user5 = user_factory('db', name='GranteeUser2', password='pass')
test_user6 = user_factory('db', name='UserForGranteeRole2', password='pass')

test_role1 = role_factory('db', name='TableSPDDLRole')
test_role2 = role_factory('db', name='GranteeRole')
test_role3 = role_factory('db', name='GranteeRole2')


@pytest.mark.version('>=6.0')
def test_1(act: Action, test_user1: User, test_user2: User, test_user3: User, test_user4: User, test_user5: User, test_user6: User, test_role1: Role, test_role2: Role, test_role3: Role, tmpdir: Path):
    stdout = ""
    import shutil

    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'
    ts3_file = tmpdir / 'tablespace3.dat'
    ts4_file = tmpdir / 'tablespace4.dat'
    ts5_file = tmpdir / 'tablespace5.dat'

    script = """
    GRANT TableSPDDLRole TO UserWithRole;

    GRANT GranteeRole TO UserWithRole2;
    commit;

    GRANT GranteeRole2 TO UserForGranteeRole2;
    commit;

    CREATE TABLESPACE TS1 FILE '%s';
    commit;

    GRANT ALTER ANY TABLESPACE TO TableSPDDLUser WITH GRANT OPTION;
    GRANT ALTER ANY TABLESPACE TO TableSPDDLRole WITH GRANT OPTION;
    commit;
    """ % ts1_file
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'], input=script, credentials=False)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'TableSPDDLUser', '-password', 'pass', '-q'],
             input="GRANT ALTER ANY TABLESPACE TO GranteeUser;", credentials=False)
    stdout += act.stdout
    act.reset()
    act.isql(switches=['-user', 'UserWithRole', '-password', 'pass', '-role', 'TableSPDDLRole', '-q'],
             input="GRANT ALTER ANY TABLESPACE TO GranteeRole;", credentials=False)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'TableSPDDLUser', '-password', 'pass', '-q'],
             input="GRANT ALTER ANY TABLESPACE TO GranteeRole2;", credentials=False)
    stdout += act.stdout
    act.reset()
    act.isql(switches=['-user', 'UserWithRole', '-password', 'pass', '-role', 'TableSPDDLRole', '-q'],
             input="GRANT ALTER ANY TABLESPACE TO GranteeUser2;", credentials=False)
    stdout += act.stdout

    shutil.copyfile(ts1_file, ts2_file)
    act.reset()
    act.isql(switches=['-user', 'GranteeUser', '-password', 'pass', '-q'],
             input="ALTER TABLESPACE TS1 SET FILE '%s';" % ts2_file, credentials=False)
    stdout += act.stdout

    shutil.copyfile(ts2_file, ts3_file)
    act.reset()
    act.isql(switches=['-user', 'UserWithRole2', '-password', 'pass', '-role', 'GranteeRole', '-q'],
             input="ALTER TABLESPACE TS1 SET FILE '%s';" % ts3_file, credentials=False)
    stdout += act.stdout

    shutil.copyfile(ts3_file, ts4_file)
    act.reset()
    act.isql(switches=['-user', 'GranteeUser2', '-password', 'pass', '-q'],
             input="ALTER TABLESPACE TS1 SET FILE '%s';" % ts4_file, credentials=False)
    stdout += act.stdout

    shutil.copyfile(ts4_file, ts5_file)
    act.reset()
    act.isql(switches=['-user', 'UserForGranteeRole2', '-password', 'pass', '-role', 'GranteeRole2',
             '-q'], input="ALTER TABLESPACE TS1 SET FILE '%s';" % ts5_file, credentials=False)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input="""DROP ROLE TableSPDDLRole; DROP ROLE GranteeRole; DROP ROLE GranteeRole2;""", credentials=False)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input="""DROP TABLESPACE TS1;""", credentials=False)
    stdout += act.stdout

    act.expected_stdout = expected_stdout
    act.stdout = stdout
    assert act.clean_stdout == act.clean_expected_stdout
