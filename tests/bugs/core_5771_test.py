#coding:utf-8
#
# id:           bugs.core_5771
# title:        Restore (without replace) when database already exists crashes gbak or Firebird (when run through service manager)
# decription:   
#                   Confirmed bug on 4.0.0.918 (as described in the ticket; 3.x is not affected).
#                 
# tracker_id:   CORE-5771
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import difflib
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
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  def svc_get_fb_log( f_fb_log ):
#  
#    global subprocess
#  
#    subprocess.call( [ context['fbsvcmgr_path'],
#                       "localhost:service_mgr",
#                       "action_get_fb_log"
#                     ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  
#  tmpfbk = 'tmp_core_5771.fbk'
#  tmpfbk='$(DATABASE_LOCATION)'+tmpfbk
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_5771_restored.fdb'
#  
#  runProgram('gbak',['-b', dsn, tmpfbk])
#  runProgram('gbak',['-rep', tmpfbk, 'localhost:'+tmpfdb])
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_5771_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_5771_check_restored.log'), 'w')
#  f_restore_err=open( os.path.join(context['temp_directory'],'tmp_5771_check_restored.err'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "action_restore",
#                   "bkp_file", tmpfbk,
#                   "dbname", tmpfdb,
#                   "verbose"
#                  ],
#                  stdout=f_restore_log, 
#                  stderr=f_restore_err)
#  flush_and_close( f_restore_log )
#  flush_and_close( f_restore_err )
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_5771_fblog_after.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  
#  # Compare firebird.log versions BEFORE and AFTER this test:
#  ######################
#  
#  oldfb=open(f_fblog_before.name, 'r')
#  newfb=open(f_fblog_after.name, 'r')
#  
#  difftext = ''.join(difflib.unified_diff(
#      oldfb.readlines(), 
#      newfb.readlines()
#    ))
#  oldfb.close()
#  newfb.close()
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5771_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  # Check logs:
#  #############
#  with open( f_restore_log.name,'r') as f:
#      for line in f:
#          line=line.replace('$(DATABASE_LOCATION)','')
#          print( 'RESTORE STDOUT:' + ' '.join( line.split() ).upper() )
#  
#  with open( f_restore_err.name,'r') as f:
#      for line in f:
#          line=line.replace('$(DATABASE_LOCATION)','')
#          print( 'RESTORE STDERR: ' + ' '.join( line.split() ).upper() )
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+'):
#              print( 'UNEXPECTED DIFF IN FIREBIRD.LOG: ' + (' '.join(line.split()).upper()) )
#  
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_restore_log,f_restore_err,f_fblog_before,f_fblog_after,f_diff_txt,tmpfbk,tmpfdb) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESTORE STDOUT:GBAK:OPENED FILE TMP_CORE_5771.FBK
    RESTORE STDERR: DATABASE TMP_5771_RESTORED.FDB ALREADY EXISTS. TO REPLACE IT, USE THE -REP SWITCH
    RESTORE STDERR: -EXITING BEFORE COMPLETION DUE TO ERRORS
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


