#coding:utf-8
#
# id:           bugs.core_4472
# title:        Message "Modifying function <F> which is currently in use" when running script with AUTODDL=OFF and <F> is called from INTERNAL function declared in other unit
# decription:   
#                  Test call delivering of firebird.log TWICE: before and after running ISQL.
#                  Then we compare only size of obtained logs rather than content (differencs of size should be zero).
#                  Result on WI-V3.0.0.32239, WI-V3.0.0.32239: Ok.
#               
#                  Result on WI-T3.0.0.30809 (Alpha2): 
#                       Unexpected call to register plugin Remote, type 2 - ignored
#                       Unexpected call to register plugin Loopback, type 2 - ignored
#                       Unexpected call to register plugin Legacy_Auth, type 12 - ignored
#                       Unexpected call to register plugin Srp, type 12 - ignored
#                       Unexpected call to register plugin Win_Sspi, type 12 - ignored
#                       Unexpected call to register plugin Arc4, type 16 - ignored
#                       INET/inet_error: read errno = 10054
#                       Modifying function FN_01 which is currently in use by active user requests
#               
#                  13.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 3.0.8.33445, 4.0.0.2416
#                     Linux:   3.0.8.33426, 4.0.0.2416
#                
# tracker_id:   CORE-4472
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
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
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  
#  fb_log_before=open( os.path.join(context['temp_directory'],'tmp_fb_log_4472_before.log'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr","action_get_fb_log"],
#                         stdout=fb_log_before, stderr=subprocess.STDOUT)
#  flush_and_close( fb_log_before )
#  
#  sqltxt='''
#      set autoddl off;
#      commit;
#      set term ^;
#      create or alter function fn_01() returns int
#      as begin
#         return 1;
#      end
#      ^
#  
#      create or alter procedure sp_01
#      as
#          declare function fn_internal_01 returns int as
#          begin
#            if ( fn_01() > 0 ) then return 1;
#            else return 0;
#          end
#      begin
#      end
#      ^
#      set term ;^
#      commit; 
#  '''
#  
#  f_sqllog=open( os.path.join(context['temp_directory'],'tmp_isql_4472.log'), 'w')
#  f_sqllog.close()
#  runProgram('isql',[ dsn, '-q','-m','-o',f_sqllog.name],sqltxt)
#  
#  fb_log_after=open( os.path.join(context['temp_directory'],'tmp_fb_log_4472_after.log'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr", "action_get_fb_log"],
#                         stdout=fb_log_after, stderr=subprocess.STDOUT)
#  flush_and_close( fb_log_after )
#  
#  # This log should be EMPTY:
#  with open( f_sqllog.name,'r') as f:
#      for line in f:
#          if line.split() and not 'Database:' in line:
#              # This line must be ignored:
#              # Database: localhost/3333:C:\\FBTESTING\\qa
#  bt-repo	mpugs.core_4472.fdb, User: SYSDBA
#              print('UNEXPECTED: ' + line)
#  
#  
#  # This difference should be ZERO:
#  fb_log_diff=os.path.getsize(fb_log_after.name)-os.path.getsize(fb_log_before.name)
#  
#  if fb_log_diff == 0:
#    print("OK: log was not changed.")
#  else:
#    print("BAD: log was increased by "+str(fb_log_diff)+" bytes.")
#  
#  #####################################################################
#  # Cleanup:
#  
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  
#  cleanup( (fb_log_before, fb_log_after, f_sqllog ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OK: log was not changed.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


