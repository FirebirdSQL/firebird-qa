#coding:utf-8
#
# id:           functional.syspriv.drop_database
# title:        Check ability to DROP database by non-sysdba user who is granted with necessary system privileges.
# decription:   
#                  We make backup and restore of current DB to other name ('functional.syspriv.drop_database.tmp'). 
#                  Than we attach to DB 'functional.syspriv.drop_database.tmp' as user U01 and try to DROP it.
#                  This should NOT raise any error, database file should be deleted from disk.
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

substitutions_1 = [('DB_NAME.*FUNCTIONAL.SYSPRIV.DROP_DATABASE.TMP', 'DB_NAME FUNCTIONAL.SYSPRIV.DROP_DATABASE.TMP')]

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

    grant select on v_check to public;
    commit;

    create or alter user u01 password '123' revoke admin role;
    revoke all on all from u01;
    commit;

    set term ^;
    execute block as
    begin
      execute statement 'drop role role_for_drop_this_database';
      when any do begin end
    end^
    set term ;^
    commit;

    create role role_for_drop_this_database set system privileges to DROP_DATABASE;
    commit;
    grant default role_for_drop_this_database to user u01;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
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
#  f_backup_restore=open( os.path.join(context['temp_directory'],'tmp_drop_db_backup_restore.log'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "user","SYSDBA","password","masterkey",
#                   "action_backup",
#                   "dbname",   fdb_this,
#                   "bkp_file", fbk_name,
#                   "verbose"],
#                   stdout=f_backup_restore, 
#                   stderr=subprocess.STDOUT
#                  )
#  
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "user","SYSDBA","password","masterkey",
#                   "action_restore", "res_replace", 
#                   "verbose", 
#                   "bkp_file", fbk_name, 
#                   "dbname", fdb_test],
#                  stdout=f_backup_restore, 
#                  stderr=subprocess.STDOUT
#                )
#  flush_and_close( f_backup_restore )
#  
#  
#  # Check that non-sysdba user can connect and DROP database <fdb_test>
#  #######
#  sql_chk='''
#      set list on; 
#      set count on; 
#      select * from v_check;
#      commit;
#      drop database;
#  '''
#  
#  runProgram('isql',['localhost:'+fdb_test,'-user','U01', '-pas', '123'], sql_chk)
#  
#  if os.path.isfile(fdb_test):
#      print('ERROR WHILE DROP DATABASE: FILE REMAINS ON DISK!')
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (fbk_name, fdb_test, f_backup_restore) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DB_NAME                         FUNCTIONAL.SYSPRIV.DROP_DATABASE.TMP
    WHO_AMI                         U01
    RDB$ROLE_NAME                   RDB$ADMIN
    RDB_ROLE_IN_USE                 <false>
    RDB$SYSTEM_PRIVILEGES           FFFFFFFFFFFFFFFF

    DB_NAME                         FUNCTIONAL.SYSPRIV.DROP_DATABASE.TMP
    WHO_AMI                         U01
    RDB$ROLE_NAME                   ROLE_FOR_DROP_THIS_DATABASE
    RDB_ROLE_IN_USE                 <true>
    RDB$SYSTEM_PRIVILEGES           0004000000000000
    Records affected: 2
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


