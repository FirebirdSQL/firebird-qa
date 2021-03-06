#coding:utf-8
#
# id:           bugs.core_2940
# title:        Trace output could contain garbage data left from filtered out statements
# decription:   
#                  1. Obtain engine_version from built-in context variable.
#                  2. Make config for trace in proper format according to FB engine version, with 'exclude_filter' parameter from ticket.
#                  3. Launch trace session in separate child process using 'FBSVCMGR action_trace_start'
#                  4. Run ISQL with test commands. Only one of these command does not contain token that is specified in 'exclude_filter'
#                  5. Stop trace session. Output its log with filtering only statistics info.
#               
#                  Checked on: WI-V2.5.5.26916 (SS, SC, CS); WI-V3.0.0.32008 (SS, SC, CS). Result: OK.
#                  Checked on: 3.0.1.32525, 4.0.0.238 // 07-jun-2016
#                  ::: NB :::
#                  Several delays (time.sleep) added in main thread because of OS buffering. Couldn't switch this buffering off.
#               
#               
#                  ::: NB ::: 07-jun-2016.
#               
#                  WI-T4.0.0.238 will issue in trace log following statement with its statistics ("1 records fetched"):
#                  ===
#                  with recursive role_tree as (     
#                    select rdb$relation_name as nm, 0 as ur from rdb$user_privileges         
#                    where 
#                        rdb$privilege = 'M' and rdb$field_name = 'D' 
#                        and rdb$user = ?  and rdb$user_type = 8     
#                    union all     
#                    select rdb$role_name as nm, 1 as ur from rdb$roles         
#                    where rdb$role_name =...
#               
#                  param0 = varchar(93), "SYSDBA"
#                  param1 = varchar(93), "NONE"
#                  ===
#                  We have to SKIP this statement statistics and start to check only "our" selects from rdb$database
#                  see usage of first_sttm_pattern and trace_stat_pattern.
#                
# tracker_id:   CORE-2940
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('^((?!records fetched).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#  from subprocess import Popen
#  import time
#  import re
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  engine=str(db_conn.engine_version)
#  db_conn.close()
#  
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
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  
#  #--------------------------------------------
#  
#  
#  txt25 = '''# Trace config, format for 2.5. Generated auto, do not edit!
#  <database %[\\\\\\\\/]bugs.core_2940.fdb>
#    enabled true
#    #include_filter
#    exclude_filter %no_trace%
#    log_connections true
#    log_transactions true
#    log_statement_finish true
#    print_plan true
#    print_perf true
#    time_threshold 0 
#  </database>
#  '''
#  
#  # NOTES ABOUT TRACE CONFIG FOR 3.0:
#  # 1) Header contains `database` clause in different format vs FB 2.5: its data must be enclosed with '{' '}'
#  # 2) Name and value must be separated by EQUALITY sign ('=') in FB-3 trace.conf, otherwise we get runtime error:
#  #    element "<. . .>" have no attribute value set
#  
#  txt30 = '''# Trace config, format for 3.0. Generated auto, do not edit!
#  database=%[\\\\\\\\/]bugs.core_2940.fdb
#  {
#    enabled = true
#    #include_filter
#    exclude_filter = %no_trace%
#    log_connections = true
#    log_transactions = true
#    log_statement_finish = true
#    print_plan = true
#    print_perf = true
#    time_threshold = 0 
#  }
#  '''
#  trccfg=open( os.path.join(context['temp_directory'],'tmp_trace_2940.cfg'), 'w')
#  if engine.startswith('2.5'):
#      trccfg.write(txt25)
#  else:
#      trccfg.write(txt30)
#  trccfg.close()
#  
#  trclog=open( os.path.join(context['temp_directory'],'tmp_trace_2940.log'), 'w')
#  trclog.close()
#  trclst=open( os.path.join(context['temp_directory'],'tmp_trace_2940.lst'), 'w')
#  trclst.close()
#  
#  #####################################################
#  # Starting trace session in new child process (async.):
#  
#  f_trclog=open(trclog.name,'w')
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_trace=Popen([context['fbsvcmgr_path'], "localhost:service_mgr",
#                 "action_trace_start",
#                  "trc_cfg", trccfg.name],
#                  stdout=f_trclog, stderr=subprocess.STDOUT)
#  
#  # Wait! Trace session is initialized not instantly!
#  time.sleep(1)
#  
#  #####################################################
#  # Running ISQL with test commands:
#  
#  sqltxt='''
#      set list on;
#      -- statistics for this statement SHOULD appear in trace log:
#      select 1 k1 from rdb$database; 
#      commit;
#  
#      -- statistics for this statement should NOT appear in trace log:
#      select 2 k2 from rdb$types rows 2 /* no_trace*/; 
#  
#      -- statistics for this statement should NOT appear in trace log:
#      select 3 no_trace from rdb$types rows 3; 
#  
#      -- statistics for this statement should NOT appear in trace log:
#      set term ^;
#      execute block returns(k4 int) as
#      begin
#         for select 4 from rdb$types rows 4 into k4 do suspend;
#      end -- no_trace
#      ^
#      set term ;^
#  '''
#  
#  runProgram('isql',[dsn,'-n'],sqltxt)
#  
#  # do NOT remove this otherwise trace log can contain only message about its start before being closed!
#  time.sleep(3)
#  
#  #####################################################
#  # Getting ID of launched trace session and STOP it:
#  
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  f_trclst=open(trclst.name,'w')
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_list"],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  trcssn=0
#  with open( trclst.name,'r') as f:
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
#  f_trclst=open(trclst.name,'a')
#  f_trclst.seek(0,2)
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_stop",
#                   "trc_id",trcssn],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  # Terminate child process of launched trace session (though it should already be killed):
#  p_trace.terminate()
#  flush_and_close( f_trclog )
#  
#  #####################################################
#  # Output log of trace session, with filtering only info about statistics ('fetches'):
#  
#  first_sttm_pattern=re.compile("select 1 k1")
#  trace_stat_pattern=re.compile("1 records fetched")
#  flag=0
#  with open( trclog.name,'r') as f:
#      for line in f:
#          if first_sttm_pattern.match(line):
#              flag=1
#          if flag==1 and trace_stat_pattern.match(line):
#              print(line)
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  
#  cleanup([i.name for i in (trccfg,trclst,trclog)])
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1 records fetched
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


