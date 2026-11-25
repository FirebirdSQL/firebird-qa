# coding:utf-8

"""
ID:          security.ddl_testing.tablespace.drop_withoutgrant
TITLE:       Deleting a tablespace without granting privileges
DESCRIPTION: 
"""

import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()
act = python_act('db')

expected_stdout = """
Statement failed, SQLSTATE = 28000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-no permission for DROP access to TABLESPACE "TS1"
-Effective user is TABLESPDDLUSER

Statement failed, SQLSTATE = 28000
unsuccessful metadata update
-DROP TABLESPACE TS2 failed
-no permission for DROP access to TABLESPACE "TS2"
-Effective user is USERWITHROLE
"""

test_user1 = user_factory('db', name='TableSPDDLUser', password='pass')
test_user2 = user_factory('db', name='UserWithRole', password='pass')

test_role1 = role_factory('db', name='TableSPDDLRole')


@pytest.mark.version('>=6.0')
def test_1(act: Action, test_user1: User, test_user2: User, test_role1: Role, tmpdir: Path):
    stdout = ""

    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    script = """
    GRANT TableSPDDLRole TO UserWithRole;
    commit;

    CREATE TABLESPACE TS1 FILE '%s';
    CREATE TABLESPACE TS2 FILE '%s';
    commit;
    """ % (ts1_file, ts2_file)
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input=script, credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'TableSPDDLUser', '-password', 'pass', '-q'],
             input="DROP TABLESPACE TS1;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'UserWithRole', '-password', 'pass', '-role', 'TableSPDDLRole', '-q'],
             input="DROP TABLESPACE TS2;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input="Drop tablespace ts1; Drop tablespace ts2;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.expected_stdout = expected_stdout
    act.stdout = stdout
    assert act.clean_stdout == act.clean_expected_stdout
