#coding:utf-8
#
# id:           bugs.core_6000
# title:        gbak issues "Your user name and password are not defined" when command switch "-fe(tch_password) ..." is specified when run as service
# decription:   
#                  ::: NOTE :::
#                  Presense of ISC_PASSWORD variable had higher priority than '-fe password_file' command switch before this ticket was fixed.
#                  This means that command "gbak -se ... -fe <file_with_invalid_password>" PASSED without errors!
#               
#                  Test creates two files, one with correct SYSDBA password and second with invalid (hope that such password: T0t@1lywr0ng - is not in use for SYSDBA).
#                  Also, test exports default SYSDBA password ('masterkey' ) to ISC_PASSWORD variable.
#                  Then we do following:
#                  1) "gbak -fe <invalid_password_file>" - this should FAIL with issuing "user name and password are not defined" in STDERR, 
#                      despite that ISC_USER isnot empty and contains valid password
#                  2) UNSET variable ISC_PASSWORD and run "gbak -fe <correct_password_file>" - this should PASS without any STDOUT or STDERR.
#               
#                  Confirmed wrong behaviour on: 4.0.0.1627, 3.0.5.33178
#                  Works fine on: 4.0.0.1629, 3.438s; 3.0.5.33179, 2.859s.
#                
# tracker_id:   CORE-6000
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  from subprocess import Popen
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_fdb =  db_conn.database_name
#  this_fbk=os.path.join(context['temp_directory'],'tmp_core_6000.fbk')
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
#  
#  cleanup( this_fbk, )
#  
#  f_psw_correct=open( os.path.join(context['temp_directory'],'tmp_psw_6000__OK.dat'), 'w')
#  f_psw_correct.write( user_password )
#  flush_and_close( f_psw_correct )
#  
#  f_psw_invalid=open( os.path.join(context['temp_directory'],'tmp_psw_6000_BAD.dat'), 'w')
#  f_psw_invalid.write( 'T0t@1lywr0ng' )
#  flush_and_close( f_psw_invalid )
#  
#  #---------------------- backup with '-fe <invalid_password_file>' --------------------------
#  
#  f_log_invalid = open( os.path.join(context['temp_directory'],'tmp_isql_6000_BAD.log'), 'w')
#  f_err_invalid = open( os.path.join(context['temp_directory'],'tmp_isql_6000_BAD.err'), 'w')
#  
#  subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', '-user', user_name ,'-fe', f_psw_invalid.name, this_fdb, this_fbk ],
#                   stdout=f_log_invalid,
#                   stderr=f_err_invalid
#                 )
#  flush_and_close( f_err_invalid )
#  flush_and_close( f_log_invalid )
#  
#  #---------------------- backup with '-fe <correct_password_file>' --------------------------
#  
#  del os.environ["ISC_PASSWORD"]
#  
#  f_log_correct = open( os.path.join(context['temp_directory'],'tmp_isql_6000__OK.log'), 'w')
#  f_err_correct = open( os.path.join(context['temp_directory'],'tmp_isql_6000__OK.err'), 'w')
#  
#  subprocess.call( [context['gbak_path'], '-b', '-se', 'localhost:service_mgr', '-user', user_name ,'-fe', f_psw_correct.name, this_fdb, this_fbk ],
#                   stdout=f_log_correct,
#                   stderr=f_err_correct
#                 )
#  flush_and_close( f_err_correct )
#  flush_and_close( f_log_correct )
#  
#  # This file should be EMPTY:
#  ###########################
#  with open(f_log_invalid.name) as f:
#      for line in f:
#          print('UNEXPECTED STDOUT FOR INVALID PASSWORD: '+line)
#  
#  with open(f_err_invalid.name) as f:
#      for line in f:
#          print('EXPECTED STDERR FOR INVALID PASSWORD: '+line)
#  
#  with open(f_log_correct.name) as f:
#      for line in f:
#          print('UNEXPECTED STDOUT FOR CORRECT PASSWORD: '+line)
#  
#  with open(f_err_correct.name) as f:
#      for line in f:
#          print('UNEXPECTED STDERR FOR CORRECT PASSWORD: '+line)
#  
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( ( f_psw_correct, f_psw_invalid, f_log_correct, f_err_correct, f_log_invalid, f_err_invalid, this_fbk ) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXPECTED STDERR FOR INVALID PASSWORD: gbak: ERROR:Your user name and password are not defined. Ask your database administrator to set up a Firebird login.
    EXPECTED STDERR FOR INVALID PASSWORD: gbak:Exiting before completion due to errors
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


