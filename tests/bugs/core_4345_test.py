#coding:utf-8
#
# id:           bugs.core_4345
# title:        Ability to trace stored functions execution
# decription:   
#                  Test checks two cases: 1) when execution of function is ENABLED and 2) DISABLED.
#                  In 1st case we search in trace log rows which prove that function execution was actually logged,
#                  and in 2nd case we have to ensure that trace log does NOT contain text about this event.
#                  Both standalone and packaged functions are checked.
#               
#                  Checked on WI-V3.0.0.32328 (SS/SC/CS); WI-T4.0.0.633
#               
#                  08-may-2017.
#                  Refactored: additional filtering using regexp (pattern.search(line)) in order to avoid take in account 
#                  start transaction events in trace (number of starting Tx became differ since 29-mar-2017 when some changes 
#                  in PIPE mechanism were done, see: 
#                  https://github.com/FirebirdSQL/firebird/commit/e1232d8015b199e33391dd2550e7c5f7e3f08493 )
#               
#                
# tracker_id:   CORE-4345
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!PARAM0|EXECUTE_FUNCTION_START|EXECUTE_FUNCTION_FINISH|SA_FUNC|PG_FUNC).)*$', ''), ('LOG_FUNC_ENABLED.*EXECUTE_FUNCTION_START', 'LOG_FUNC_ENABLED EXECUTE_FUNCTION_START'), ('LOG_FUNC_ENABLED.*EXECUTE_FUNCTION_FINISH', 'LOG_FUNC_ENABLED EXECUTE_FUNCTION_FINISH')]

init_script_1 = """
    set term ^;
    create or alter function sa_func(a int) returns bigint as
    begin
      return a * a;
    end
    ^
    recreate package pg_test as
    begin
        function pg_func(a int) returns bigint;
    end
    ^
    create package body pg_test as
    begin
        function pg_func(a int) returns bigint as
        begin
            return a * a;
        end
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  import shutil
#  import re
#  
#  trace_timestamp_prefix='[.*\\s+]*20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3,4}\\s+\\(.+\\)'
#  func_start_ptn=re.compile(  trace_timestamp_prefix + '\\s+(FAILED){0,1}\\s*EXECUTE_FUNCTION_START$', re.IGNORECASE)
#  func_finish_ptn=re.compile( trace_timestamp_prefix + '\\s+(FAILED){0,1}\\s*EXECUTE_FUNCTION_FINISH$', re.IGNORECASE)
#  func_name_ptn=re.compile('Function\\s+(SA_FUNC|PG_TEST.PG_FUNC):$')
#  func_param_prn=re.compile('param[0-9]+\\s+=\\s+', re.IGNORECASE)
#  
#  
#  db_conn.close()
#  
#  # Minimal delay after we issue command fbsvcmgr action_trace_start
#  # and before we launch execution of checked code
#  ###########################################
#  min_delay_after_trace_start = 1
#  
#  # Minimal delay after we finish connection to database
#  # and before issuing command to stop trace
#  ##########################################
#  min_delay_before_trace_stop = 1
#  
#  # Minimal delay for trace log be flushed on disk after
#  # we issue command 'fbsvcmgr action_trace_stop':
#  ###############################
#  min_delay_after_trace_stop = 1
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  def make_trace_config( is_func_logged, trccfg_name ):
#  
#      # NOTES ABOUT TRACE CONFIG FOR 3.0:
#      # 1) Header contains `database` clause in different format vs FB 2.5: its data must be enclosed with '{' '}'
#      # 2) Name and value must be separated by EQUALITY sign ('=') in FB-3 trace.conf, otherwise we get runtime error:
#      #    element "<. . .>" have no attribute value set
#      
#      if is_func_logged.upper() == 'TRUE':
#          txt30 = '''
#          database=%[\\\\\\\\/]bugs.core_4345.fdb
#          {
#            enabled		=	true
#            time_threshold	=	0
#            log_connections	=	true
#            log_transactions	=	true
#            log_function_start	=	true
#            log_function_finish	=	true
#          }
#          '''
#      else:
#          txt30 = '''
#          database=%[\\\\\\\\/]bugs.core_4345.fdb
#          {
#            enabled		=	true
#            time_threshold	=	0
#            log_connections	=	true
#            log_transactions	=	true
#            log_function_start	=	false
#          }
#          '''
#  
#      trccfg=open( trccfg_name, 'w')
#      trccfg.write(txt30)
#      trccfg.close()
#  
#      return
#  
#  def stop_trace_session():
#  
#      # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#      import os
#      import subprocess
#  
#      f_trclst=open( os.path.join(context['temp_directory'],'tmp_trace_4345.lst'), 'w')
#      subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr", "action_trace_list"],
#                       stdout=f_trclst,
#                       stderr=subprocess.STDOUT
#                     )
#      f_trclst.close()
#      
#      trcssn=0
#      with open( f_trclst.name,'r') as f:
#          for line in f:
#              if 'Session ID' in line:
#                  trcssn=line.split()[2]
#                  break
#      f.close()
#      
#      # Result: `trcssn` is ID of active trace session. Now we have to terminate it:
#      f_trclst=open(f_trclst.name,'a')
#      f_trclst.seek(0,2)
#      subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr", "action_trace_stop", "trc_id",trcssn],
#                       stdout=f_trclst, stderr=subprocess.STDOUT
#                     )
#      f_trclst.close()
#  
#      os.remove(f_trclst.name)
#  
#      return
#  
#  
#  sql_fnc='''
#      set list on;
#      set term ^;
#      execute block as -- returns( sa_func_result bigint, pg_func_result bigint ) as
#          declare sa_func_result bigint;
#          declare pg_func_result bigint;
#      begin
#          sa_func_result = sa_func( %s );
#          pg_func_result = pg_test.pg_func( %s );
#          --suspend;
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  # % (123, 456)
#  
#  
#  ##############################################################################
#  ###                                                                        ###
#  ###             C A S E - 1:     l o g _ f u n c    =   t r u e            ###
#  ###                                                                        ###
#  ##############################################################################
#  
#  # Make trace config with ENABLING logging of func. execution:
#  
#  trccfg_log_enable=os.path.join(context['temp_directory'],'tmp_trace_4345_log_enable.cfg')
#  
#  make_trace_config( 'true', trccfg_log_enable )
#  
#  f_trclog_log_enable=open( os.path.join(context['temp_directory'],'tmp_trace_4345_log_enable.log'), 'w')
#  
#  #####################################################
#  # Starting trace session in new child process (async.):
#  
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_trace=Popen( [ context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_start",
#                   "trc_cfg", trccfg_log_enable
#                 ],
#                 stdout=f_trclog_log_enable,
#                 stderr=subprocess.STDOUT
#               )
#  
#  # Wait _AT_LEAST_ 4..5 seconds in 2.5 because trace session is initialized not instantly.
#  # If this delay is less then 2 second then trace log will be EMPTY (got on 2.5 SS and Cs).
#  time.sleep( min_delay_after_trace_start )
#  
#  ####################################################
#  # Make connection to database and perform script that 
#  # calls two functions: standalone and packaged:
#  ####################################################
#  
#  runProgram('isql',[dsn, '-n', '-q'], sql_fnc % (123, 456) )
#  
#  # do NOT remove this otherwise trace log can contain only message about its start before being closed!
#  time.sleep(min_delay_before_trace_stop)
#  
#  #####################################################
#  # Getting ID of launched trace session and STOP it:
#  
#  stop_trace_session()
#  time.sleep(min_delay_after_trace_stop)
#  
#  # Terminate child process of launched trace session (though it should already be killed):
#  p_trace.terminate()
#  f_trclog_log_enable.close()
#  
#  
#  #############
#  # O U T P U T
#  #############
#  
#  with open( f_trclog_log_enable.name,'r') as f:
#      for line in f:
#          if ( func_start_ptn.search(line) 
#               or func_finish_ptn.search(line) 
#               or func_name_ptn.search(line) 
#               or func_param_prn.search(line) ):
#              print('LOG_FUNC_ENABLED '+line.upper())
#  f.close()
#  
#  #############################################################################
#  ###                                                                       ###
#  ###             C A S E - 2:     l o g _ f u n c   =   f al s e           ###
#  ###                                                                       ###
#  #############################################################################
#  
#  # Make trace config with DISABLING logging of func. execution:
#  
#  trccfg_log_disable=os.path.join(context['temp_directory'],'tmp_trace_4345_log_disable.cfg')
#  make_trace_config( 'false', trccfg_log_disable )
#  
#  #####################################################
#  # Starting trace session in new child process (async.):
#  
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  
#  f_trclog_log_disable=open( os.path.join(context['temp_directory'],'tmp_trace_4345_log_disable.log'), 'w')
#  
#  p_trace=Popen( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                  "action_trace_start",
#                   "trc_cfg", trccfg_log_disable
#                 ],
#                 stdout=f_trclog_log_disable,
#                 stderr=subprocess.STDOUT
#               )
#  
#  # Wait _AT_LEAST_ 4..5 seconds in 2.5 because trace session is initialized not instantly.
#  # If this delay is less then 2 second then trace log will be EMPTY (got on 2.5 SS and Cs).
#  
#  time.sleep( min_delay_after_trace_start )
#  
#  
#  ####################################################
#  # Make connection to database and perform script that 
#  # calls two functions: standalone and packaged:
#  ####################################################
#  
#  runProgram('isql',[dsn, '-n', '-q'], sql_fnc % (789, 987)  )
#  
#  # do NOT remove this otherwise trace log can contain only message about its start before being closed!
#  time.sleep(min_delay_before_trace_stop)
#  
#  #####################################################
#  # Getting ID of launched trace session and STOP it:
#  stop_trace_session()
#  time.sleep(min_delay_after_trace_stop)
#  
#  
#  # Terminate child process of launched trace session (though it should already be killed):
#  p_trace.terminate()
#  f_trclog_log_disable.close()
#  
#  #############
#  # O U T P U T
#  #############
#  
#  with open( f_trclog_log_disable.name,'r') as f:
#      for line in f:
#          if ( func_start_ptn.search(line) 
#             or func_finish_ptn.search(line) 
#             or func_name_ptn.search(line) 
#             or func_param_prn.search(line) ):
#              print('LOG_FUNC_DISABLED '+line.upper())
#  f.close()
#  
#  time.sleep(1)
#  
#  ###############################
#  # Cleanup.
#  
#  f_list = (f_trclog_log_enable, f_trclog_log_disable)
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#  
#  os.remove(trccfg_log_enable)
#  os.remove(trccfg_log_disable)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    LOG_FUNC_ENABLED 2016-02-10T15:10:43.5940 (1700:00C52280) EXECUTE_FUNCTION_START
    LOG_FUNC_ENABLED FUNCTION SA_FUNC:
    LOG_FUNC_ENABLED PARAM0 = INTEGER, "123"
    LOG_FUNC_ENABLED 2016-02-10T15:10:43.5940 (1700:00C52280) EXECUTE_FUNCTION_FINISH
    LOG_FUNC_ENABLED FUNCTION SA_FUNC:
    LOG_FUNC_ENABLED PARAM0 = INTEGER, "123"
    LOG_FUNC_ENABLED PARAM0 = BIGINT, "15129"
    LOG_FUNC_ENABLED 2016-02-10T15:10:43.5940 (1700:00C52280) EXECUTE_FUNCTION_START
    LOG_FUNC_ENABLED FUNCTION PG_TEST.PG_FUNC:
    LOG_FUNC_ENABLED PARAM0 = INTEGER, "456"
    LOG_FUNC_ENABLED 2016-02-10T15:10:43.5940 (1700:00C52280) EXECUTE_FUNCTION_FINISH
    LOG_FUNC_ENABLED FUNCTION PG_TEST.PG_FUNC:
    LOG_FUNC_ENABLED PARAM0 = INTEGER, "456"
    LOG_FUNC_ENABLED PARAM0 = BIGINT, "207936"
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


