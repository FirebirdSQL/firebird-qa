#coding:utf-8
#
# id:           functional.services.role_in_service_attachment
# title:        Check that trace plugin shows ROLE used in service attachment. Format: USER[:ROLE].
# decription:   
#                   See: https://github.com/FirebirdSQL/firebird/commit/dd241208f203e54a9c5e9b8b24c0ef24a4298713
#                   Checked on 4.0.0.2070 SS/CS.
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         

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
#  import sys
#  import os
#  import re
#  import subprocess
#  import time
#  from fdb import services
#  from subprocess import Popen
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  f_sql_cmd = open( os.path.join(context['temp_directory'],'tmp_trace_prepare.sql'), 'w', buffering=0)
#  f_sql_txt='''
#    set wng off;
#    set bail on;
#    create or alter user tmp$watcher password '123' using plugin Srp;
#    revoke all on all from tmp$watcher;
#    commit;
#    set term ^;
#    execute block as
#    begin
#        execute statement 'drop role r4watch';
#        when any do begin end
#    end
#    ^
#    set term ;^
#    commit;
#    -- Trace other users' attachments
#    create role r4watch set system privileges to TRACE_ANY_ATTACHMENT;
#    commit;
#    grant default r4watch to user tmp$watcher;
#    commit;
#  '''
#  f_sql_cmd.write(f_sql_txt)
#  flush_and_close(f_sql_cmd)
#  
#  f_prepare_log=open( os.path.join(context['temp_directory'],'tmp_trace_prepare.log'), 'w', buffering=0)
#  subprocess.call( [ context['isql_path'], dsn, "-i", f_sql_cmd.name ], stdout=f_prepare_log, stderr=subprocess.STDOUT )
#  flush_and_close(f_prepare_log)
#  
#  txt = '''
#      database=
#      {
#          enabled = false
#      }
#      services 
#      {
#          enabled = true
#          log_initfini = false
#          include_filter = "%(Start|Stop) Trace Session%"
#          log_services = true
#          log_errors = true
#          log_warnings = false
#      }
#  
#  '''
#  
#  f_trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trace_test.cfg'), 'w', buffering = 0)
#  f_trc_cfg.write(txt)
#  flush_and_close(f_trc_cfg)
#  
#  # ##############################################################
#  # S T A R T   T R A C E   i n   S E P A R A T E    P R O C E S S
#  # ##############################################################
#  
#  f_trc_log=open( os.path.join(context['temp_directory'],'tmp_trace_test.log'), "w", buffering = 0)
#  f_trc_err=open( os.path.join(context['temp_directory'],'tmp_trace_test.err'), "w", buffering = 0)
#  
#  # ::: NB ::: DO NOT USE 'localhost:service_mgr' here! Use only local protocol:
#  p_trace = Popen( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'user', 'tmp$watcher', 'password', '123', 'role', 'r4watch', 'action_trace_start' , 'trc_cfg', f_trc_cfg.name],stdout=f_trc_log,stderr=f_trc_err)
#  
#  time.sleep(1)
#  
#  # ####################################################
#  # G E T  A C T I V E   T R A C E   S E S S I O N   I D
#  # ####################################################
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  
#  f_trc_lst = open( os.path.join(context['temp_directory'],'tmp_trace_test.lst'), 'w', buffering = 0)
#  subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_list'], stdout=f_trc_lst)
#  flush_and_close(f_trc_lst)
#  
#  # !!! DO NOT REMOVE THIS LINE !!!
#  time.sleep(1)
#  
#  trcssn=0
#  with open( f_trc_lst.name,'r') as f:
#      for line in f:
#          i=1
#          if 'Session ID' in line:
#              for word in line.split():
#                  if i==3:
#                      trcssn=word
#                  i=i+1
#              break
#  # Result: `trcssn` is ID of active trace session. Now we have to terminate it:
#  
#  # Here we are waiting for trace log will be fulfilled with data related to SERVICE activity, namely: trace session that was just started.
#  time.sleep(3)
#  
#  # ####################################################
#  # S E N D   R E Q U E S T    T R A C E   T O   S T O P
#  # ####################################################
#  if trcssn>0:
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_stop','trc_id', trcssn], stdout=fn_nul)
#      fn_nul.close()
#      # DO NOT REMOVE THIS LINE:
#      time.sleep(1)
#  
#  p_trace.terminate()
#  flush_and_close(f_trc_log)
#  flush_and_close(f_trc_err)
#  
#  p_new = re.compile('service_mgr.*\\s+tmp\\$watcher:r4watch,.*', re.IGNORECASE)
#  p_old = re.compile('service_mgr.*\\s+tmp\\$watcher,.*', re.IGNORECASE)
#  
#  # Check:
#  #########
#  # Log of preparation .sql must be empty:
#  with open( f_prepare_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED output in '+f_prepare_log.name+': '+line)
#  
#  # Trace STDOUT must contain line like: 
#  # service_mgr, (Service 0000000004F893C0, TMP$WATCHER:r4watch, TCPv6:::1/55274, C:\\FB SS
#  bsvcmgr.exe:6752)
#  with open( f_trc_log.name,'r') as f:
#    for line in f:
#        if 'service_mgr' in line:
#            if p_new.search(line):
#                print('EXPECTED output found in the trace log')
#            elif p_old.search(line):
#                print('ERROR: trace output contains only USER, without ROLE.')
#            else:
#                print('ERROR: format in the trace log differs from expected.')
#  
#  # Trace STDERR must be empty:
#  with open( f_trc_err.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED STDERR in '+f_trc_err.name+': '+line)
#  
#  
#  # Cleanup:
#  ###########
#  cleanup( ( f_sql_cmd, f_prepare_log, f_trc_log, f_trc_err, f_trc_cfg, f_trc_lst ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXPECTED output found in the trace log
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


