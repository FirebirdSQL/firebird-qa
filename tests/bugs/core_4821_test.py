#coding:utf-8

"""
ID:          issue-5118
ISSUE:       5118
TITLE:       Incorrect results when left join on subquery with constant column
DESCRIPTION:
  ::: NOTE ::: Test requires that databases.conf contains 'RemoteAccess = true' for security.db
  This line is added there by scenario '<QA_HOME>\\rundaily.bat' every time when check new FB snapshot.

  We make connection to security.db and create there user and role, with granting this role to user.
  (so, ROLE also is stored in the security.db).
  Then we grant privilege to create DB to just created role.
  After this we check that:
  * user can NOT create database if 'ROLE <this_role>' missed in the 'create database' statement;
  * user _CAN_ create database when issues: create database ... user ... password ... ROLE <this_role>

  Then we create backup of just created database and check that:
  * user can NOT restore it until specifying '-ROLE <this_role>' in gbak command line;
  * user _CAN_ restore database when issues: gbak -rep ... -user ... -pas ... -ROLE <this_role>;
  * the same pair of checks is performed for fbsvcmgr invocation;

  Finally, we connect again to security.db and drop <this_role>. After this restore must not be allowed
  even when "ROLE <this_role>" is specified in commands gbak or fbsvcmgr.
NOTES:
[24.11.2021] pcisar
  Without change to databases.conf this test FAILs because it's not possible to grant create
  database to role tmp$db_creator although it exists (in test database):
   Statement failed, SQLSTATE = 28000
   unsuccessful metadata update
   -GRANT failed
   -SQL role TMP$DB_CREATOR does not exist
   -in security database
JIRA:        CORE-4821
"""

import pytest
import sys
from pathlib import Path
from firebird.qa import *

# version: 3.0.5

substitutions = [('no permission for CREATE access to DATABASE .*',
                  'no permission for CREATE access to DATABASE'),
                 ('gbak: ERROR:failed to create database .*',
                  'gbak: ERROR:failed to create database'),
                 ('-failed to create database .*', '-failed to create database'),
                 ('CREATED_DB_NAME .*', 'CREATED_DB_NAME'),
                 ('FDB_RESTORED_USING_GBAK .*', 'FDB_RESTORED_USING_GBAK'),
                 ('FDB_RESTORED_USING_SMGR .*', 'FDB_RESTORED_USING_SMGR')]

db = db_factory()

tmp_user = user_factory('db', name='tmp$c4821_boss', password='123')
test_role = role_factory('db', name='tmp$db_creator')

act = python_act('db', substitutions=substitutions)

fdb_test1 = temp_file('tmp_4821_test1.fdb')
fdb_test2 = temp_file('tmp_4821_test2.fdb')
fbk_name = temp_file('tmp_4821_test2.fbk')
fdb_restored_using_gbak = temp_file('tmp_4821_restored.gbak.fdb')
fdb_restored_using_smgr = temp_file('tmp_4821_restored.smgr.fdb')
fdb_restored_unexpected = temp_file('tmp_4821_restored.no_grant.fdb')

expected_stdout = """
    CREATED_DB_NAME                 /opt/scripts/qa-rundaily/dbg-repo/tmp/tmp_4821_test2.fdb
    FDB_RESTORED_USING_GBAK         /opt/scripts/qa-rundaily/dbg-repo/tmp/tmp_4821_restored.gbak.fdb
    FDB_RESTORED_USING_SMGR         /opt/scripts/qa-rundaily/dbg-repo/tmp/tmp_4821_restored.smgr.fdb
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for CREATE access to DATABASE
    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database
    gbak:Exiting before completion due to errors
    no permission for CREATE access to DATABASE
    -failed to create database
    -Exiting before completion due to errors
    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database
    gbak:Exiting before completion due to errors
    no permission for CREATE access to DATABASE
    -failed to create database
    -Exiting before completion due to errors
"""

@pytest.mark.skip("FIXME: databases.conf")
@pytest.mark.version('>=3.0.5')
def test_1(act: Action, tmp_user: User, capsys, fdb_test1: Path, fdb_test2: Path,
           fbk_name: Path, fdb_restored_using_gbak: Path, fdb_restored_using_smgr: Path,
           fdb_restored_unexpected: Path, test_role: Role):
    # The role MUST be created in security database!
    #with act.db.connect() as con:
        #con.execute_immediate(f'grant create database to role {test_role.name}')
    with act.db.connect() as con:
        con.execute_immediate(f'grant create database to role {test_role.name}')
        con.execute_immediate(f'grant {test_role.name} to {tmp_user.name}')
        con.commit()
    #
    sql_test = f"""
    create database 'localhost:{fdb_test1}' user {tmp_user.name} password '123';
    select mon$database_name as created_db_name from mon$database;
    rollback;
    create database 'localhost:{fdb_test2}' user {tmp_user.name} password '123' role {test_role.name};
    set list on;
    select mon$database_name as created_db_name from mon$database;
    """
    act.isql(switches=['-q'], input=sql_test)
    print(act.stdout)
    # Must PASS because user tmp_user is the owner of this DB:
    act.reset()
    act.gbak(switches=['-b', '-user', tmp_user.name, '-pas', '123',
                         act.get_dsn(fdb_test2), str(fbk_name)],
               credentials=False)
    # Must FAIL because we do not specify role, with text:
    # "gbak: ERROR:no permission for CREATE access to DATABASE ... / gbak: ERROR:failed to create database localhost:tmp_4821_restored.gbak.fdb"
    act.reset()
    act.expected_stderr = "Must FAIL because we do not specify role"
    act.gbak(switches=['-rep', '-user', tmp_user.name, '-pas', '123',
                         str(fbk_name), act.get_dsn(fdb_restored_using_gbak)],
               credentials=False)
    print(act.stderr, file=sys.stderr)
    # Must PASS because we DO specify role:
    act.reset()
    act.gbak(switches=['-rep', '-user', tmp_user.name, '-pas', '123', '-role', test_role.name,
                         str(fbk_name), act.get_dsn(fdb_restored_using_gbak)],
               credentials=False)
    #
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password,
                         act.get_dsn(fdb_restored_using_gbak)], connect_db=False,
               input='set list on; select mon$database_name as fdb_restored_using_gbak from mon$database;')
    print(act.stdout)
    # Must FAIL because we do not specify role, with text: "no permission for CREATE access to DATABASE ... / failed to create database tmp_4821_restored.smgr.fdb"
    act.reset()
    act.expected_stderr = "Must FAIL because we do not specify role"
    act.svcmgr(switches=[f'{act.host}:service_mgr', 'user', tmp_user.name, 'password', '123',
                           'action_restore', 'res_replace', 'bkp_file', str(fbk_name),
                           'dbname', str(fdb_restored_using_smgr)], connect_mngr=False)
    print(act.stderr, file=sys.stderr)
    # Must PASS because we DO specify role:
    act.reset()
    act.svcmgr(switches=[f'{act.host}:service_mgr', 'user', tmp_user.name, 'password', '123',
                           'role', test_role.name,  'action_restore', 'res_replace',
                           'bkp_file', str(fbk_name), 'dbname', str(fdb_restored_using_smgr)],
                 connect_mngr=False)
    #
    act.reset()
    act.isql(switches=['-user', act.db.user, '-password', act.db.password,
                         act.get_dsn(fdb_restored_using_gbak)], connect_db=False,
               input='set list on; select mon$database_name as fdb_restored_using_smgr from mon$database;')
    print(act.stdout)
    #
    act.reset()
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.stdout = capsys.readouterr().out
    act.stderr = capsys.readouterr().err
    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)
