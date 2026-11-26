# coding:utf-8

"""
ID:          security.ddl_testing.tablespace.create_aftergrant
TITLE:       Creating a tablespace after granting privileges
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

test_role1 = role_factory('db', name='TableSPDDLRole')


@pytest.mark.version('>=6.0')
def test_1(act: Action, test_user1: User, test_user2: User, test_role1: Role, tmpdir: Path):
    stdout = ""

    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    script = """
    GRANT TableSPDDLRole TO UserWithRole;
    commit;

    GRANT CREATE TABLESPACE TO TableSPDDLUser;
    GRANT CREATE TABLESPACE TO TableSPDDLRole;
    commit;
    """
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'], input=script, credentials=False)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', 'TableSPDDLUser', '-password', 'pass', '-q'],
             input="CREATE TABLESPACE TS1 FILE '%s';" % ts1_file, credentials=False)
    stdout += act.stdout
    act.reset()
    act.isql(switches=['-user', 'UserWithRole', '-password', 'pass', '-role', 'TableSPDDLRole', '-q'],
             input="CREATE TABLESPACE TS2 FILE '%s';" % ts2_file, credentials=False)
    stdout += act.stdout

    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password, '-q'],
             input="Drop tablespace ts1; Drop tablespace ts2;", credentials=False, combine_output=True)
    stdout += act.stdout

    act.expected_stdout = expected_stdout
    act.stdout = stdout
    assert act.clean_stdout == act.clean_expected_stdout
