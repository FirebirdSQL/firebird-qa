#coding:utf-8

"""
ID:          syspriv.access-shutdown-database
TITLE:       Check ability to access to database in shutdown single mode as non-sysdba
DESCRIPTION:
  We create role with granting system privilege ACCESS_SHUTDOWN_DATABASE to it.
  Then we create user and make this role as DEFAULT to him.
  Then we check that user 'TMP_SYSPRIV_USER':
      1. can NOT CHANGE database attribute, i.e. can NOT shutdown or bring online database;
      2. CAN make attachment to DB in 'shutdown single maintenace' mode and make some DML there.
  Also, we check that while 'TMP_SYSPRIV_USER' is connected, NO other attachment is possible.
  This is done by trying to make ES EDS as SYSDBA - this should fail with "335544528 : database shutdown".

  Checked on 4.0.0.267. See also letter from Alex 23.06.2016 11:46.
FBTEST:      functional.syspriv.access_shutdown_database

NOTES: checked on 4.0.1.2692, 5.0.0.489.
"""
import os
import pytest
from firebird.qa import *
from firebird.driver import ShutdownMode,ShutdownMethod,SrvStatFlag,DatabaseError
#from firebird.driver.types import DatabaseError

for v in ('ISC_USER','ISC_PASSWORD'):
    try:
        del os.environ[ v ]
    except KeyError as e:
        pass

substitutions = [ ('no permission for (shutdown|(bring online)) access to database .*', 'no permission for shutdown/online access to database')
                  ,('-Some database.* shutdown when trying to read mapping data', '')   # <<< perhaps this is due to bug in Classic. May need to be deleted later // 25.09.2022
                  ,('335544528 : database.* shutdown', '335544528 : database shutdown')
                  ,('Data source : Firebird::localhost:.*', 'Data source : Firebird::localhost:')
                  ,('-At block line: [\\d]+, col: [\\d]+', '-At block line')
                ]
db = db_factory()

tmp_user = user_factory('db', name='tmp_syspriv_user', password='123')
tmp_role = role_factory('db', name='tmp_role_for_access_shutdown_db')

act = python_act('db', substitutions=substitutions)

expected_stdout_fbsvc = """
    no permission for shutdown/online access to database
"""

expected_stdout_isql = """
    WHO_AMI                         TMP_SYSPRIV_USER
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB_ROLE_IN_USE                 <false>
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF
    MON$SHUTDOWN_MODE               2
    WHO_AMI                         TMP_SYSPRIV_USER
    RDB$ROLE_NAME                   TMP_ROLE_FOR_ACCESS_SHUTDOWN_DB
    RDB_ROLE_IN_USE                 <true>
    RDB$SYSTEM_PRIVILEGES           0001000000000000
    MON$SHUTDOWN_MODE               2
    ATT_USER                        TMP_SYSPRIV_USER
    ATT_PROT                        TCP

    Statement failed, SQLSTATE = 42000
    Execute statement error at attach :
    335544528 : database shutdown
    Data source : Firebird::localhost:
    -At block line
"""

@pytest.mark.es_eds
@pytest.mark.version('>=4.0')

#--------------------------------------------------------------------

def show_db_info(act: Action, tmp_user: User, tmp_role: Role):

    print('Data from DB header:')
    with act.connect_server(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as srv:
        srv.database.get_statistics(database = act.db.db_path, flags = SrvStatFlag.HDR_PAGES)
        stat_output = [x.rstrip() for x in srv.readlines() if x.strip()]
        for i,line in enumerate(stat_output):
            if 'database' in line.lower() or 'attributes' in line.lower():
                print(line)

    print('Data from mon$database:')
    with act.db.connect(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as con:
        cur = con.cursor()
        cur.execute('select mon$database_name,mon$shutdown_mode,mon$read_only,mon$creation_date,mon$owner,mon$sec_database from mon$database')
        hdr=cur.description
        for r in cur:
            for i in range(len(hdr)):
                print( hdr[i][0].ljust(32),':', r[i] )

#--------------------------------------------------------------------

def test_1(act: Action, tmp_user: User, tmp_role:Role, capsys):

    init_script = \
    f'''
        set wng off;
        create or alter view v_check as
        select
             current_user as who_ami
            ,r.rdb$role_name
            ,rdb$role_in_use(r.rdb$role_name) as RDB_ROLE_IN_USE
            ,r.rdb$system_privileges
            ,m.mon$shutdown_mode
        from mon$database m cross join rdb$roles r;
        commit;

        alter user {tmp_user.name} revoke admin role;
        revoke all on all from {tmp_user.name};

        create or alter trigger trg_connect active on connect as
        begin
        end;
        commit;

        recreate table att_log (
            att_id int,
            att_name varchar(255),
            att_user varchar(255),
            att_prot varchar(255)
        );

        commit;

        grant select on v_check to public;
        grant all on att_log to public;
        commit;

        set term ^;
        create or alter trigger trg_connect active on connect as
        begin
          if ( upper(current_user) <> upper('SYSDBA') ) then
             in autonomous transaction do
             insert into att_log(att_name, att_user, att_prot)
             select
                  mon$attachment_name
                 ,mon$user
                 ,left(mon$remote_protocol,3)
             from mon$attachments
             where mon$user = current_user
             ;
        end
        ^
        set term ;^
        commit;

        alter role {tmp_role.name}
            set system privileges to ACCESS_SHUTDOWN_DATABASE; -- CHANGE_SHUTDOWN_MODE, USE_GFIX_UTILITY, IGNORE_DB_TRIGGERS;
        commit;
        grant default {tmp_role.name} to user {tmp_user.name};
        commit;
    '''
    act.isql(switches=['-q'], input=init_script, combine_output = True)
    assert '' == act.stdout, 'Init script failed.'
    act.reset()

    # ---------------------------------------------------------------

    # Must FAIL: user has right only to *access* to DB in shutdown-single mode and make some DMLs there.
    # But he has NO right to change DB state to shutdown (any kind of mode).
    # Expected error: "no permission for shutdown/online access to database ..."
    with act.connect_server(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as srv_nondba:
        try:
            srv_nondba.database.shutdown(database=act.db.db_path
                                  ,mode=ShutdownMode.SINGLE
                                  ,method=ShutdownMethod.FORCED
                                  ,timeout=0)
            print('### CAUTION ### database.shutdown() UNEXPECTEDLY NOT RAISED ERROR.')
            show_db_info(act, tmp_user, tmp_role)
        except DatabaseError as e:
            print(e.__str__())

    act.expected_stdout = expected_stdout_fbsvc
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout # <<<<<<<<<<<<<<<<<<<<<<<< check #0
    act.reset()

    #-----------------------------------------------------------------

    # Must PASS: we change DB state to shut-single using SYSDBA account.
    # No message must be issued now:
    with act.connect_server() as srv_sysdba:
        try:
            srv_sysdba.database.shutdown(database=act.db.db_path
                                  ,mode=ShutdownMode.SINGLE
                                  ,method=ShutdownMethod.FORCED
                                  ,timeout=0)
        
        except DatabaseError as e:
            print(e.__str__())

    act.expected_stdout = ''
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout # <<<<<<<<<<<<<<<<<<<<<<<< check #1
    act.reset()

    # ---------------------------------------------------------------
    # Result: DB now is in shutdown-single mode.
    # We have to check that only single attachment can be established to this DB:

    sql_chk='''
        set list on;
        select v.* from v_check v;
        select a.att_user, att_prot from att_log a;
        set term ^;
        execute block returns( who_else_here rdb$user ) as
            declare another_user varchar(31);
        begin
            execute statement 'select current_user from rdb$database'
            on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
            as user 'SYSDBA' password 'masterkey'
            into who_else_here;

            suspend;
        end
        ^
        set term ;^
    '''
    act.isql(switches=['-q', '-user', tmp_user.name, '-pas', tmp_user.password, '-role', tmp_role.name], input=sql_chk, credentials = False, combine_output=True)

    act.expected_stdout = expected_stdout_isql
    assert act.clean_stdout == act.clean_expected_stdout  # <<<<<<<<<<<<<<<<<<<<<<<< check #2
    act.reset()

    # ---------------------------------------------------------------

    # must FAIL: we attempt to bring DB online using NON-dba account:
    # Expected error: "no permission for bring online access to database ..."
    # !!!NB!!! As of 25.09.2022, for FB 4.x and 5.x in Classic mode additional message will raise here:
    # "-Some database(s) were shutdown when trying to read mapping data"
    # Sent report to Alex et al, 25.09.2022 18:55. Waiting for resolution.
    #
    with act.connect_server(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as srv_nondba:
        try:
            srv_nondba.database.bring_online(database=act.db.db_path)
            print('### CAUTION ### database.bring_online() UNEXPECTEDLY NOT RAISED ERROR.')
            show_db_info(act, tmp_user, tmp_role)
        except DatabaseError as e:
            print(e.__str__())

    act.expected_stdout = expected_stdout_fbsvc # 'no permission for shutdown/online access to database'
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout # <<<<<<<<<<<<<<<<<<<<<<<< check #3
    act.reset()

    # must PASS because here we return DB online using SYSDBA account:
    with act.connect_server() as srv_sysdba:
        try:
            srv_sysdba.database.bring_online(database=act.db.db_path)
        
        except DatabaseError as e:
            print(e.__str__())

    assert '' == capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout # <<<<<<<<<<<<<<<<<<<<<<<< check #4
    act.reset()
