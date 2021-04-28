#coding:utf-8
#
# id:           bugs.core_4319
# title:        Engine crashes when trace config contains line "connection_id=NN" and we attempt to connect to non-existent database/alias
# decription:   
#                  Test receives version of FB (2.5 or 3.0) and prepares text file that will serve as TRACE config.
#                  This text file will contain trivial content appropriate to FB version with 'connection_id=NNN' key.
#               
#                  Than we make async start of trace session using FBTRACEMGR utility and after small pause (~1 sec)
#                  run ISQL with attempt to make connect to non-existent alias.
#               
#                  Confirmed crash on WI-T3.0.0.30566 (Alpha 1). Note: utility fbsvcmgr can not start when trace config 
#                  contains connection_id: standard Windows crash report appears with such data:
#                  ...
#                  AppName: fbsvcmgr.exe	 AppVer: 3.0.0.30566	 ModName: msvcr100.dll
#                  ModVer: 10.0.30319.1	 Offset: 0008ae6e
#                  ...
#                
# tracker_id:   CORE-4319
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('TRACE SESSION ID.*', 'TRACE SESSION ID')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version, 2.5 or 3.0, for make trace config in appropriate format:
#  engine=str(db_conn.engine_version)
#  db_conn.close()
#  
#  #-----------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      os.fsync(file_handle.fileno())
#  
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  
#  txt25 = '''# Trace config, format for 2.5. Generated auto, do not edit!
#  <database %[\\\\\\\\/]bugs.core_4319.fdb>
#    enabled true
#    log_errors true
#    time_threshold 0 
#    connection_id 1234
#    log_connections true
#  </database>
#  '''
#  
#  # NOTES ABOUT TRACE CONFIG FOR 3.0:
#  # 1) Header contains `database` clause in different format vs FB 2.5: its data must be enclosed with '{' '}'
#  # 2) Name and value must be separated by EQUALITY sign ('=') in FB-3 trace.conf, otherwise we get runtime error:
#  #    element "<. . .>" have no attribute value set
#  
#  txt30 = '''# Trace config, format for 3.0. Generated auto, do not edit!
#  database=%[\\\\\\\\/]bugs.core_4319.fdb
#  {
#    enabled = true
#    log_errors = true
#    time_threshold = 0
#    connection_id = 1234
#    log_connections = true
#  }
#  '''
#  
#  f_trccfg=open( os.path.join(context['temp_directory'],'tmp_trace_4319.cfg'), 'w')
#  if engine.startswith('2.5'):
#      f_trccfg.write(txt25)
#  else:
#      f_trccfg.write(txt30)
#  flush_and_close( f_trccfg )
#  
#  #####################################################
#  # Starting trace session in new child process (async.):
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  
#  f_trclog=open( os.path.join(context['temp_directory'],'tmp_trace_4319.log'), 'w')
#  p_trace=Popen([ context['fbtracemgr_path'],
#                  "-se", "localhost:service_mgr",
#                  "-sta", "-c", f_trccfg.name],
#                  stdout=f_trclog, stderr=subprocess.STDOUT)
#  
#  # Wait! Trace session is initialized not instantly!
#  time.sleep(1)
#  
#  
#  f_sqltxt=open( os.path.join(context['temp_directory'],'tmp_connect_4319.sql'), 'w')
#  f_sqltxt.write("connect 'localhost:some_non_existent' user 'SYSDBA' password 'masterkey'; show database; show version;")
#  flush_and_close( f_sqltxt )
#  
#  f_sqllog=open( os.path.join(context['temp_directory'],'tmp_connect_4319.log'), 'w')
#  p_isql = subprocess.call([ context['isql_path'], dsn, "-i", f_sqltxt.name ],
#                             stdout=f_sqllog, stderr=subprocess.STDOUT)
#  flush_and_close( f_sqllog )
#  
#  # Terminate child process of launched trace session:
#  
#  time.sleep(1)
#  
#  p_trace.terminate()
#  flush_and_close( f_trclog )
#  
#  with open( f_trclog.name,'r') as f:
#      for line in f:
#          print(line.upper())
#  
#  with open( f_sqllog.name,'r') as f:
#      for line in f:
#          if 'SQLSTATE = 08001' in line:
#              print(line.upper())
#  
#  # CLEANUP
#  ##########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_sqltxt, f_sqllog, f_trccfg, f_trclog)] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TRACE SESSION ID STARTED
    STATEMENT FAILED, SQLSTATE = 08001
  """

@pytest.mark.version('>=2.5.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


