#coding:utf-8
#
# id:           bugs.core_5273
# title:        Crash when attempt to create database with running trace ( internal Firebird consistency check (cannot find tip page (165), file: tra.cpp line: 2233) )
# decription:   
#                   1. Get the content of firebird.log before test.
#                   2. Make config file and launch trace session, with separate logging of its STDOUT and STDERR.
#                   3. Make DDLfile and run ISQL, with separate logging of its STDOUT and STDERR.
#                   4. Stop trace session
#                   5. Get the content of firebird.log after test.
#                   6. Ensure that files which should store STDERR results are empty.
#                   7. Ensure that there is no difference in the content of firebird.log.
#                       
#                   Confirmed on 4.0.0.254 (SS, SC):
#                   1) unexpected STDERR logs:
#                       + Unexpected STDERR, file ...	mp_5273_ddl.err: Statement failed, SQLSTATE = 08006
#                       + Unexpected STDERR, file ...	mp_5273_ddl.err: Error reading data from the connection.
#                       + Unexpected STDERR, file ...	mp_5273_ddl.err: After line 3 in file ...	mp_5273_ddl.sql
#                       + Unexpected STDERR, file ...	mp_trace_5273.err: Error reading data from the connection.
#                   2) diff in firebird.log:
#                       +CSPROG	Thu Jun 16 14:17:13 2016
#                       +	Database: C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\TMP_5273.FDB
#                       +	internal Firebird consistency check (cannot find tip page (165), file: tra.cpp line: 2233)
#                       +
#                       +
#                       +CSPROG	Thu Jun 16 14:17:13 2016
#                       +	INET/inet_error: read errno = 10054, server host = localhost, address = 127.0.0.1/3430
#               
#                   Works fine on 4.0.0.256.
#                
# tracker_id:   CORE-5273
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
# import os
#  import time
#  import subprocess
#  import difflib
#  from subprocess import Popen
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
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
#  def svc_get_fb_log( f_fb_log ):
#  
#    global subprocess
#  
#    subprocess.call([ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      "action_get_fb_log"
#                    ],
#                     stdout=f_fb_log, 
#                     stderr=subprocess.STDOUT
#                   )
#  
#    return
#  
#  
#  
#  
#  tmpfdb1=os.path.join(context['temp_directory'],'tmp_5273.fdb')
#  cleanup( tmpfdb1, )
#  
#  sql_ddl='''    set list on;
#      set bail on;
#      create database 'localhost:%(tmpfdb1)s';
#      select mon$database_name from mon$database;
#      commit;
#      drop database;
#  ''' % locals()
#  
#  trace_options = '''# Trace config, format for 3.0 and above. Generated auto, do not edit!
#  database=%[\\\\\\\\/]tmp_5273.fdb
#  {
#    enabled = true
#    log_sweep = true
#    log_errors = true
#    time_threshold = 0
#    log_connections = true
#    log_transactions = true
#    log_statement_prepare = true
#    log_statement_start = true
#    log_statement_finish = true
#    log_statement_free = true
#    log_trigger_start = true
#    log_trigger_finish = true
#    print_perf = true
#    max_sql_length = 16384
#    max_log_size = 5000000
#  }
#  services
#  {
#    enabled = false
#    log_services = true
#    log_service_query = true
#    log_errors = true
#  } 
#  '''
#  f_trccfg=open( os.path.join(context['temp_directory'],'tmp_trace_5273.cfg'), 'w')
#  f_trccfg.write(trace_options)
#  flush_and_close( f_trccfg )
#  
#  # Get content of firebird.log BEFORE test:
#  ##########################################
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_5273_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  
#  # Starting trace session in new child process (async.):
#  #######################################################
#  
#  f_trclog=open( os.path.join(context['temp_directory'],'tmp_trace_5273.log'), 'w')
#  f_trcerr=open( os.path.join(context['temp_directory'],'tmp_trace_5273.err'), 'w')
#  
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_trace=Popen([context['fbsvcmgr_path'], "localhost:service_mgr",
#                 "action_trace_start",
#                  "trc_cfg", f_trccfg.name],
#                  stdout=f_trclog, 
#                  stderr=f_trcerr
#               )
#  
#  # Wait! Trace session is initialized not instantly!
#  time.sleep(2)
#  
#  f_create_db_sql = open( os.path.join(context['temp_directory'],'tmp_5273_ddl.sql'), 'w')
#  f_create_db_sql.write(sql_ddl)
#  flush_and_close( f_create_db_sql )
#  
#  
#  # CREATE DATABASE 
#  #################
#  
#  f_create_db_log = open( os.path.join(context['temp_directory'],'tmp_5273_ddl.log'), 'w')
#  f_create_db_err = open( os.path.join(context['temp_directory'],'tmp_5273_ddl.err'), 'w')
#  subprocess.call( [context['isql_path'], "-q", "-i", f_create_db_sql.name ],
#                   stdout = f_create_db_log,
#                   stderr = f_create_db_err
#                 )
#  flush_and_close( f_create_db_log )
#  flush_and_close( f_create_db_err )
#  
#  
#  #####################################################
#  # Getting ID of launched trace session and STOP it:
#  
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  f_trclst=open( os.path.join(context['temp_directory'],'tmp_trace_5273.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
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
#  f_trclst=open(f_trclst.name,'a')
#  f_trclst.seek(0,2)
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_stop",
#                   "trc_id",trcssn],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  # 23.02.2021. DELAY FOR AT LEAST 1 SECOND REQUIRED HERE!
#  # On windows preliminary termination of running trace before it completes 'stop' request leads to:
#  #    INET/inet_error: read errno = 10054, client host = ..., address = ::1/62963, user = ...
#  time.sleep(1)
#  
#  # Terminate child process of launched trace session (though it should already be killed):
#  p_trace.terminate()
#  flush_and_close( f_trclog )
#  flush_and_close( f_trcerr )
#  
#  
#  # Get content of firebird.log AFTER test:
#  #########################################
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_5273_fblog_after.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  # STDERR for ISQL (that created DB) and trace session - they both must be EMPTY:
#  #################
#  f_list=[f_create_db_err, f_trcerr]
#  for i in range(len(f_list)):
#     f_name=f_list[i].name
#     if os.path.getsize(f_name) > 0:
#         with open( f_name,'r') as f:
#             for line in f:
#                 print("Unexpected STDERR, file "+f_name+": "+line)
#  
#  # DIFFERENCE in the content of firebird.log should be EMPTY:
#  ####################
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5273_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          print("Unexpected DIFF in firebird.log: "+line)
#  
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_create_db_sql, f_create_db_log, f_create_db_err, f_trccfg, f_trclst, f_trclog, f_trcerr,f_fblog_before,f_fblog_after,f_diff_txt, tmpfdb1) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


