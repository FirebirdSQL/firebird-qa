# coding:utf-8

"""
ID:          security.ddl_testing.tablespace.create_withoutgrant
TITLE:       Creating a tablespace without privileges
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
-CREATE TABLESPACE TS1 failed
-No permission for CREATE TABLESPACE operation

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLESPACE TS2 failed
-No permission for CREATE TABLESPACE operation

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-Tablespace TS1 not found

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE TS2 failed
-Tablespace TS2 not found

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
    """
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input=script, credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'TableSPDDLUser', '-password', 'pass', '-q'],
             input="CREATE TABLESPACE TS1 FILE '%s';" % ts1_file, credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'UserWithRole', '-password', 'pass', '-role', 'TableSPDDLRole', '-q'],
             input="CREATE TABLESPACE TS2 FILE '%s';" % ts2_file, credentials=False, combine_output=True)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input=" DROP TABLESPACE TS1; DROP TABLESPACE TS2;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.expected_stdout = expected_stdout
    act.stdout = stdout
    assert act.clean_stdout == act.clean_expected_stdout
