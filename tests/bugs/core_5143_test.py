#coding:utf-8
#
# id:           bugs.core_5143
# title:        internal Firebird consistency check (cannot find tip page (165), file: tra.cpp line: 2375)
# decription:   
#                   This .fbt does exactly what's specified in the ticket: creates database, adds objects and makes b/r.
#                   Restoring process is logged; STDOUT should not contain word 'ERROR:'; STDERR should be empty at all.
#               
#                   Confirmed:
#                   1) error on 3.0.0.32378:
#                         STDLOG: gbak: ERROR:table T2 is not defined
#                         STDLOG: gbak: ERROR:unsuccessful metadata update
#                         STDLOG: gbak: ERROR:    TABLE T2
#                         STDLOG: gbak: ERROR:    Can't have relation with only computed fields or constraints
#                         STDERR: action cancelled by trigger (0) to preserve data integrity
#                         STDERR: -could not find object for GRANT
#                         STDERR: -Exiting before completion due to errors
#                   2) OK on 3.0.0.32471, 4.0.0.127
#                
# tracker_id:   CORE-5143
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create or alter function f1 returns int as begin return 1; end
    ^
    set term ;^ 
    commit;
    
    recreate table t1 (id int);
    recreate table t2 (id int);

    set term ^;
    create or alter function f1 returns int
    as
    begin
      return (select count(*) from t1) + (select count(*) from t2);
    end^
    set term ;^ 
    commit;

  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  
#  tmpsrc = db_conn.database_name
#  tmpbkp = os.path.splitext(tmpsrc)[0] + '.fbk'
#  tmpres = os.path.splitext(tmpsrc)[0] + '.tmp'
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close(file_handle):
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
#  
#  f_backup_log=open(os.devnull, 'w')
#  f_backup_err=open( os.path.join(context['temp_directory'],'tmp_backup_5143.err'), 'w')
#  
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                    "action_backup",
#                    "dbname",   tmpsrc,
#                    "bkp_file", tmpbkp,
#                    "verbose"
#                  ],
#                  stdout=f_backup_log, 
#                  stderr=f_backup_err
#                 )
#  flush_and_close( f_backup_log )
#  flush_and_close( f_backup_err )
#  
#  f_restore_log = open( os.path.join(context['temp_directory'],'tmp_restore_5143.log'), 'w')
#  f_restore_err = open( os.path.join(context['temp_directory'],'tmp_restore_5143.err'), 'w')
#  
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                    "action_restore",
#                    "bkp_file", tmpbkp,
#                    "dbname",   tmpres,
#                    "res_replace",
#                    "res_one_at_a_time",
#                    "verbose"
#                  ],
#                  stdout=f_restore_log, 
#                  stderr=f_restore_err
#                 )
#  
#  flush_and_close( f_restore_log )
#  flush_and_close( f_restore_err )
#  
#  with open(f_backup_err.name, 'r') as f:
#      for line in f:
#          print( "STDOUT: "+line )
#  
#  # Result of this filtering should be EMPTY:
#  with open( f_restore_log.name,'r') as f:
#      for line in f:
#          if 'ERROR:' in line.upper():
#              print( "STDLOG: "+line )
#  
#  # This file should be EMPTY:
#  with open(f_restore_err.name, 'r') as f:
#      for line in f:
#          print( "STDERR: "+line )
#  
#  # Cleanup:
#  ##########
#  
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  
#  cleanup( (f_backup_log,f_backup_err,f_restore_log,f_restore_err,tmpbkp,tmpres) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


