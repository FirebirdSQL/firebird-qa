#coding:utf-8

"""
ID:          issue-5569
ISSUE:       5569
TITLE:       Error messages differ when regular user tries to RESTORE database, depending on his default role and (perhaps) system privilege USE_GBAK_UTILITY
DESCRIPTION:
JIRA:        CORE-5291
"""

import pytest
from pathlib import Path
from firebird.qa import *

substitutions = [('gbak: ERROR:no permission for CREATE access to DATABASE.*',
                  'gbak: ERROR:no permission for CREATE access to DATABASE'),
                 ('gbak: ERROR:    failed to create database.*',
                  'gbak: ERROR:    failed to create database'),
                 ('gbak: ERROR:failed to create database localhost:.*',
                  'gbak: ERROR:failed to create database localhost')]

init_script = """
    -- This is not needed anymore for new test implementation
    --
    -- set wng off;
    -- create or alter user tmp$c5291_1 password '123' revoke admin role;
    -- create or alter user tmp$c5291_2 password '456' revoke admin role;
    -- commit;
    -- revoke all on all from tmp$c5291_1;
    -- revoke all on all from tmp$c5291_2;
    -- commit;
    -- create role role_for_use_gbak_utility set system privileges to USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE;
    -- commit;
    -- grant default role_for_use_gbak_utility to user tmp$c5291_2;
    -- commit;
"""

db = db_factory(init=init_script)

user_1 = user_factory('db', name='tmp$c5291_1', password='123')
user_2 = user_factory('db', name='tmp$c5291_2', password='456')
test_role = role_factory('db', name='role_for_use_gbak_utility')

act = python_act('db', substitutions=substitutions)

fbk_file = temp_file('tmp_core_5291.fbk')
fdb_file_1 = temp_file('tmp_core_5291_1.fdb')
fdb_file_2 = temp_file('tmp_core_5291_2.fdb')

expected_stderr_1 = """
    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:    failed to create database
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database localhost
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:    failed to create database
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database localhost
    gbak:Exiting before completion due to errors
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, user_1: User, user_2: User, fbk_file: Path, fdb_file_1: Path,
           fdb_file_2: Path, test_role: Role, capsys):
    with act.db.connect() as con:
        con.execute_immediate('alter role role_for_use_gbak_utility set system privileges to USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE')
        con.commit()
        con.execute_immediate('grant default role_for_use_gbak_utility to user tmp$c5291_2')
        con.commit()
    #
    act.gbak(switches=['-b', act.db.dsn, str(fbk_file)])
    # User 1
    act.reset()
    act.expected_stderr = "We expect errors"
    act.gbak(switches=['-se', 'localhost:service_mgr', '-rep', str(fbk_file),
                       str(fdb_file_1), '-user', user_1.name, '-pas', user_1.password],
             credentials=False)
    print(act.stderr)
    # User 1
    act.reset()
    act.expected_stderr = "We expect errors"
    act.gbak(switches=['-rep', str(fbk_file), act.get_dsn(fdb_file_2),
                       '-user', user_1.name, '-pas', user_1.password], credentials=False)
    print(act.stderr)
    # User 2
    act.reset()
    act.expected_stderr = "We expect errors"
    act.gbak(switches=['-se', f'{act.host}:service_mgr', '-rep', str(fbk_file),
                       str(fdb_file_1), '-user', user_2.name, '-pas', user_2.password],
             credentials=False)
    print(act.stderr)
    # User 2
    act.reset()
    act.expected_stderr = "We expect errors"
    act.gbak(switches=['-rep', str(fbk_file), act.get_dsn(fdb_file_2),
                       '-user', user_2.name, '-pas', user_2.password], credentials=False)
    print(act.stderr)
    #
    act.reset()
    act.expected_stderr = expected_stderr_1
    act.stderr = capsys.readouterr().out
    assert act.clean_stderr == act.clean_expected_stderr
