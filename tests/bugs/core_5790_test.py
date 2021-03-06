#coding:utf-8
#
# id:           bugs.core_5790
# title:        User with DROP DATABASE privilege can't drop database
# decription:   
#                   Confirmed bug on 3.0.4.32924
#                   Works fine on:
#                      3.0.4.32947: OK, 2.906s.
#                       4.0.0.955: OK, 3.453s.
#                   07.02.2019: fixed wrong connection string which did use local protocol instead of required remote.
#                   Checked on:
#                      4.0.0.1421 CS, SC, SS
#                      3.0.5.33097 CS, SS
#                
# tracker_id:   CORE-5790
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  thisdb=db_conn.database_name
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_5790.tmp'
#  tmpusr='tmp$c5790'
#  
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
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  cleanup( (tmpfdb,) )
#  
#  sql_txt='''
#      create database 'localhost:%(tmpfdb)s';
#      alter database set linger to 0;
#      commit;
#      create or alter user %(tmpusr)s password '123';
#      commit;
#      grant drop database to tmp$c5790;
#      commit;
#      connect 'localhost:%(tmpfdb)s' user %(tmpusr)s password '123';
#      set list on;
#      set count on;
#      select
#           r.rdb$user           --           tmp$c5790
#          ,r.rdb$grantor        --           sysdba
#          ,r.rdb$privilege      --           o
#          ,r.rdb$grant_option   --           0
#          ,r.rdb$relation_name  --           sql$database
#          ,r.rdb$field_name     --           <null>
#          ,r.rdb$user_type      --           8
#          ,iif( r.rdb$object_type = decode( left(rdb$get_context('SYSTEM', 'ENGINE_VERSION'),1), '3',20, '4',21), 1, 0) "rdb_object_type_is_expected ?"
#      from rdb$user_privileges r 
#      where r.rdb$user=upper('%(tmpusr)s');
#  
#      -- this should NOT show any attachments: "Records affected: 0" must be shown here.
#      select * from mon$attachments where mon$attachment_id != current_connection;
#      commit;
#  
#      drop database;
#      rollback;
#  
#      -- !!! 07.02.2019 only remote protocol must be used here !! 
#      -- Otherwise we will attempt to make local attach to security4.fdb
#      -- 335544344 : I/O error during "CreateFile (open)" operation for file "C:\\FB SS\\SECURITY4.FDB"
#      -- 335544734 : Error while trying to open file
#      -- This is because securityN.fdb has by default linger = 60 seconds when we use SS, thus it is 
#      -- stiil kept opened by FB server process.
#  
#      connect 'localhost:%(thisdb)s'; -- OLD VERSION OF THIS TEST HAD ERROR HERE: connect '%(thisdb)s'
#      drop user %(tmpusr)s;
#      commit;
#      --set list on;
#      --set count on;
#      --set echo on;
#      --select current_user, s.* from rdb$database left join sec$users s on s.sec$user_name not containing 'SYSDBA';
#  ''' % locals()
#  
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_5790.sql'), 'w')
#  f_isql_cmd.write(sql_txt)
#  flush_and_close( f_isql_cmd )
#  
#  f_isql_log=open( os.path.join(context['temp_directory'],'tmp_5790.log'), 'w')
#  f_isql_err=open( os.path.join(context['temp_directory'],'tmp_5790.err'), 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_isql_cmd.name], stdout=f_isql_log, stderr=f_isql_err )
#  flush_and_close( f_isql_log )
#  flush_and_close( f_isql_err )
#  
#  if os.path.isfile(tmpfdb):
#      print('### ERROR ### Database file was NOT deleted!')
#      cleanup( tmpfdb, )
#  
#  with open(f_isql_log.name,'r') as f:
#      for line in f:
#          print(line)
#  
#  with open(f_isql_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED STDERR: ' + line)
#  
#  # cleanup
#  #########
#  time.sleep(1)
#  f_list = (f_isql_log,f_isql_err,f_isql_cmd)
#  cleanup( f_list )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$USER                        TMP$C5790
    RDB$GRANTOR                     SYSDBA
    RDB$PRIVILEGE                   O
    RDB$GRANT_OPTION                0
    RDB$RELATION_NAME               SQL$DATABASE
    RDB$FIELD_NAME                  <null>
    RDB$USER_TYPE                   8
    rdb_object_type_is_expected ?   1
    Records affected: 1
    Records affected: 0
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


