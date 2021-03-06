#coding:utf-8
#
# id:           functional.syspriv.trace_any_attachment
# title:        Check ability to trace any attachment by non-sysdba user who is granted with necessary system privileges.
# decription:   
#                   Checked on 4.0.0.262.
#               	03-mar-2021. Checked on:
#               		* Windows: 4.0.0.2377, 3.0.8.33420
#               		* Linux:   4.0.0.2377, 3.0.8.33415
#               
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set wng off;
    set bail on;
    create or alter user sys_tracer_for_anyone password '123' revoke admin role;
    revoke all on all from sys_tracer_for_anyone;
    commit;
    -- Trace other users' attachments
    create role role_for_trace_any_attachment 
        set system privileges to TRACE_ANY_ATTACHMENT;
    commit;
    grant default role_for_trace_any_attachment to user sys_tracer_for_anyone;
    commit;

    recreate table test_trace_any_attachment(id int);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  from subprocess import Popen
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_file=os.path.basename(db_conn.database_name)
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
#  trace_options = '''# Trace config, format for 3.0 and above. Generated auto, do not edit!
#  database=%%[\\\\\\\\/]%(db_file)s
#  {
#      enabled = true
#      log_initfini = false
#      log_errors = true
#      time_threshold = 0
#      log_statement_start = true
#      log_statement_finish = true
#      print_perf = true
#      max_sql_length = 16384
#  }
#  ''' % locals()
#  
#  f_trccfg=open( os.path.join(context['temp_directory'],'tmp_syspriv_trace_any_attacmhent.cfg'), 'w')
#  f_trccfg.write(trace_options)
#  flush_and_close( f_trccfg )
#  
#  # Starting trace session in new child process (async.):
#  #######################################################
#  
#  f_trclog=open( os.path.join(context['temp_directory'],'tmp_syspriv_trace_any_attacmhent.log'), 'w')
#  f_trcerr=open( os.path.join(context['temp_directory'],'tmp_syspriv_trace_any_attacmhent.err'), 'w')
#  
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_trace=Popen([context['fbsvcmgr_path'], "localhost:service_mgr",
#                 "user", "sys_tracer_for_anyone", "password", "123",
#                 "action_trace_start",
#                  "trc_cfg", f_trccfg.name],
#                  stdout=f_trclog, 
#                  stderr=f_trcerr
#               )
#  
#  
#  time.sleep(1)
#  
#  #####################################################
#  # Getting ID of launched trace session and STOP it:
#  
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  f_trclst=open( os.path.join(context['temp_directory'],'tmp_trace_5273.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "user", "sys_tracer_for_anyone", "password", "123",
#                   "action_trace_list"],
#                   stdout=f_trclst, 
#                   stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  trcssn=0
#  with open( f_trclst.name,'r') as f:
#      for line in f:
#          i=1
#          if 'Session ID' in line:
#              for word in line.split():
#                  if i==3:
#                      trcssn=word
#                  i=i+1
#              break
#  
#  # Result: `trcssn` is ID of active trace session. Now we have to terminate it:
#  
#  runProgram('isql',[dsn, '-q', '-n'], 'insert into test_trace_any_attachment(id) values(123456789);')
#  time.sleep(1)
#  
#  # REQUEST TRACE TO STOP:
#  ########################
#  f_trclst=open(f_trclst.name,'a')
#  f_trclst.seek(0,2)
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "user", "sys_tracer_for_anyone", "password", "123",
#                   "action_trace_stop",
#                   "trc_id",trcssn],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  time.sleep(2)
#  
#  # Terminate child process of launched trace session (though it should already be killed):
#  p_trace.terminate()
#  flush_and_close( f_trclog )
#  flush_and_close( f_trcerr )
#  
#  
#  # Must be EMPTY:
#  with open( f_trcerr.name,'r') as f:
#      for line in f:
#          print(line)
#  
#  # Must contain info about SYSDBA activity (this was traced by non-sysdba user):
#  
#  found_sysdba_attachment, found_sysdba_statement = False, False
#  with open( f_trclog.name,'r') as f:
#      for line in f:
#          if 'SYSDBA:NONE' in line:
#              if not found_sysdba_attachment:
#                  print('FOUND SYSDBA ATTACHMENT.')
#                  found_sysdba_attachment = True
#          if '123456789' in line:
#              if not found_sysdba_statement:
#                  print('FOUND SYSDBA STATEMENT.')
#                  found_sysdba_statement = True
#  
#  runProgram('isql',[dsn], 'drop user sys_tracer_for_anyone;')
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_trclst,f_trcerr,f_trclog, f_trccfg) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    FOUND SYSDBA ATTACHMENT.
    FOUND SYSDBA STATEMENT.
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


