#coding:utf-8
#
# id:           functional.syspriv.use_gbak_utility
# title:        Check ability to to make database backup.
# decription:   
#                  We create user and grant system privileges USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE to him
#                  (but revoke all other rights), and then we try to make BACKUP with attaching to database as this user (U01).
#                  Then we check that this user:
#                  1) can NOT restore .fbk to another file name (backup <> restore!)
#                  2) CAN query to the table which is not granted to him by regular GRANT statement 
#                    (restoring is done by SYSDBA).
#               
#                  Checked on 4.0.0.267.
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('.*NO PERMISSION FOR CREATE ACCESS TO DATABASE.*', 'NO PERMISSION FOR CREATE ACCESS TO DATABASE'), ('.*-FAILED TO CREATE DATABASE.*', '-FAILED TO CREATE DATABASE'), ('CLOSING FILE, COMMITTING, AND FINISHING.*', 'CLOSING FILE, COMMITTING, AND FINISHING'), ('DB_NAME.*FUNCTIONAL.SYSPRIV.USE_GBAK_UTILITY.TMP', 'DB_NAME FUNCTIONAL.SYSPRIV.USE_GBAK_UTILITY.TMP'), ('BLOB_ID.*', '')]

init_script_1 = """
    set wng off;
    set bail on;
    set list on;
    set count on;

    create or alter view v_check as
    select 
        upper(mon$database_name) as db_name
        ,current_user as who_ami
        ,r.rdb$role_name
        ,rdb$role_in_use(r.rdb$role_name) as RDB_ROLE_IN_USE
        ,r.rdb$system_privileges
    from mon$database m cross join rdb$roles r;
    commit;

    create or alter user u01 password '123' revoke admin role;
    revoke all on all from u01;
    commit;

    recreate table test(x int, b blob);
    commit;

    insert into test values(1, upper('qwertyuioplkjhgfdsazxcvbnm') );
    commit;

    grant select on v_check to public;
    --------------------------------- [ !! ] -- do NOT: grant select on test to u01; -- [ !! ] 
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role role_for_use_gbak_utility';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    -- Ability to make database backup.
    -- NB: SELECT_ANY_OBJECT_IN_DATABASE - mandatory for reading data from tables et al.
    create role role_for_use_gbak_utility 
        set system privileges to USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE;
    commit;
    grant default role_for_use_gbak_utility to user u01;
    commit;

  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  
#  db_pref = os.path.splitext(db_conn.database_name)[0]
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for f in f_names_list:
#         if type(f) == file:
#            del_name = f.name
#         elif type(f) == str:
#            del_name = f
#         else:
#            print('Unrecognized type of element:', f, ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#      
#  #--------------------------------------------
#  
#  fdb_this = db_pref+'.fdb'
#  fbk_name = db_pref+'.fbk'
#  fdb_test = db_pref+'.tmp'
#  
#  # !!! NB !!! See CORE-5291. We have to remove file that will be used as target for restoring,
#  # otherwise error msg will contain strange phrase "gbak: ERROR:could not drop ... (database might be in use)"
#  cleanup( (fdb_test,) )
#  
#  f_backup_u01_log=open( os.path.join(context['temp_directory'],'tmp_backup_u01.log'), 'w')
#  f_backup_u01_err=open( os.path.join(context['temp_directory'],'tmp_backup_u01.err'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "user","U01","password","123",
#                   "action_backup",
#                   "dbname",   fdb_this,
#                   "bkp_file", fbk_name,
#                   "verbose"],
#                   stdout=f_backup_u01_log, 
#                   stderr=f_backup_u01_err
#                  )
#  
#  flush_and_close( f_backup_u01_log )
#  flush_and_close( f_backup_u01_err )
#  
#  # NB: user U01 has right only to make BACKUP, but has NO right for RESTORING database
#  # (to restore he has to be granted with system privilege CREATE_DATABASE).
#  # Thus following attempt should be finished with ERROR:
#  # ===
#  # gbak: ERROR:no permission for CREATE access to DATABASE C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\TMP.TMP
#  # gbak: ERROR:failed to create database localhost/3400:C:\\MIX
#  irebird\\QA
#  bt-repo	mp	mp.tmp
#  # gbak:Exiting before completion due to errors
#  # ===
#  
#  f_restore_u01_log=open( os.path.join(context['temp_directory'],'tmp_restore_u01.log'), 'w')
#  f_restore_u01_err=open( os.path.join(context['temp_directory'],'tmp_restore_u01.err'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "user","U01","password","123",
#                   "action_restore", "res_replace", 
#                   "verbose", 
#                   "bkp_file", fbk_name, 
#                   "dbname", fdb_test],
#                  stdout=f_restore_u01_log, 
#                  stderr=f_restore_u01_err
#                )
#  flush_and_close( f_restore_u01_log )
#  flush_and_close( f_restore_u01_err )
#  
#  
#  # Now try to restore as SYSDBA and then check that U01 will be able 
#  # to connect to this DB and run query on table TEST:
#  
#  f_restore_sys_log=open( os.path.join(context['temp_directory'],'tmp_restore_sys.log'), 'w')
#  f_restore_sys_err=open( os.path.join(context['temp_directory'],'tmp_restore_sys.err'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "user", user_name, "password", user_password,
#                   "action_restore", "res_replace", 
#                   "verbose", 
#                   "bkp_file", fbk_name, 
#                   "dbname", fdb_test],
#                  stdout=f_restore_sys_log, 
#                  stderr=f_restore_sys_err
#                )
#  flush_and_close( f_restore_sys_log )
#  flush_and_close( f_restore_sys_err )
#  
#  
#  # Check content of logs.
#  
#  # Must be EMPTY:
#  with open( f_backup_u01_err.name,'r') as f:
#      for line in f:
#          print('U01 BACKUP STDERR: '+line.upper())
#  
#  # Must contain: "closing file, committing, and finishing"
#  with open( f_backup_u01_log.name,'r') as f:
#      for line in f:
#          if 'closing file' in line:
#              print('U01 BACKUP STDLOG: ' + ' '.join(line.split()).upper() )
#  
#  
#  # Must contain errors:
#  # no permission for CREATE access to DATABASE C:/MIX/firebird/QA/fbt-repo/tmp/functional.syspriv.use_gbak_utility.tmp
#  # -failed to create database C:/MIX/firebird/QA/fbt-repo/tmp/functional.syspriv.use_gbak_utility.tmp
#  # -Exiting before completion due to errors
#  with open( f_restore_u01_err.name,'r') as f:
#      for line in f:
#          print('U01 RESTORE STDERR: ' + ' '.join(line.split()).upper() )
#  
#  # Must contain: "finishing, closing, and going home "
#  with open( f_restore_sys_log.name,'r') as f:
#      for line in f:
#          if 'going home' in line:
#              print('SYSDBA RESTORE STDLOG: ' + ' '.join(line.split()).upper() )
#  
#  # Must be EMPTY:
#  with open( f_restore_sys_err.name,'r') as f:
#      for line in f:
#          print('SYSDBA RESTORE STDERR: '+line.upper())
#  
#  # Check that non-sysdba user can connect and query table 'test':
#  #######
#  sql_chk='''
#      set list on; 
#      set count on; 
#      set blob all;
#      select * from v_check;
#      select x,b as blob_id from test;
#      commit;
#  '''
#  
#  runProgram('isql',['localhost:'+fdb_test,'-user','U01', '-pas', '123'], sql_chk)
#  
#  # Cleanup:
#  ##########
#  runProgram('isql',[dsn,'-user',user_name, '-pas', user_password], 'drop user u01; commit;')
#  cleanup( (fbk_name, fdb_test, f_backup_u01_log,f_backup_u01_err,f_restore_u01_log,f_restore_u01_err,f_restore_sys_log,f_restore_sys_err) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    U01 BACKUP STDLOG: GBAK:CLOSING FILE, COMMITTING, AND FINISHING
    U01 RESTORE STDERR: NO PERMISSION FOR CREATE ACCESS TO DATABASE
    U01 RESTORE STDERR: -FAILED TO CREATE DATABASE
    U01 RESTORE STDERR: -EXITING BEFORE COMPLETION DUE TO ERRORS
    SYSDBA RESTORE STDLOG: GBAK:FINISHING, CLOSING, AND GOING HOME

    DB_NAME FUNCTIONAL.SYSPRIV.USE_GBAK_UTILITY.TMP
    WHO_AMI                         U01
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB_ROLE_IN_USE                 <false>
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF
    DB_NAME FUNCTIONAL.SYSPRIV.USE_GBAK_UTILITY.TMP
    WHO_AMI                         U01
    RDB$ROLE_NAME                   ROLE_FOR_USE_GBAK_UTILITY
    RDB_ROLE_IN_USE                 <true>
    RDB$SYSTEM_PRIVILEGES           0008010000000000
    Records affected: 2
    X                               1
    QWERTYUIOPLKJHGFDSAZXCVBNM
    Records affected: 1
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


