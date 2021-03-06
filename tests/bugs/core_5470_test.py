#coding:utf-8
#
# id:           bugs.core_5470
# title:        Trace INCLUDE_FILTER with [[:WHITESPACE:]]+ does not work when statement contains newline is issued
# decription:   
#                  We create a list of several DDLs which all contain NEWLINE character(s) between jeyword and name of DB object.
#                  Then we launch trace session and execute all these DDLs.
#                  Finally we check whether trace log contains every DDL or not.
#                  Expected result: text of every DDL should be FOUND in the trace log.
#               
#                  Checked on 2.5.7.27048, 3.0.2.32685, 4.0.0.531 - all fine.
#                
# tracker_id:   CORE-5470
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
#  from fdb import services
#  from subprocess import Popen
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
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
#  if engine.startswith('2.5'):
#      fb_home = fb_home + 'bin'+os.sep
#      txt = '''# Generated auto, do not edit!
#        <database %[\\\\\\\\/]security?.fdb>
#            enabled false
#        </database>
#  
#        <database %[\\\\\\\\/]bugs.core_5470.fdb>
#            enabled        true
#            time_threshold 0
#            log_initfini   false
#            log_statement_finish = true
#            include_filter = "%(recreate|create|alter|drop|comment on)[[:WHITESPACE:]]+(domain|generator|sequence|exception|procedure|table|index|view|trigger|role|filter|external function)%"
#        </database>
#      '''
#  else:
#      txt = '''# Generated auto, do not edit!
#        database=%[\\\\\\\\/]security?.fdb
#        {
#            enabled = false
#        }
#        database=%[\\\\\\\\/]bugs.core_5470.fdb
#        {
#            enabled = true
#            time_threshold = 0
#            log_initfini   = false
#            log_errors = true
#            log_statement_finish = true
#            include_filter = "%(recreate|create|alter|drop|comment on)[[:WHITESPACE:]]+(domain|generator|sequence|exception|procedure|function|table|index|view|trigger|role|filter|external function)%"
#        }
#      '''
#  
#  f_trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trc_5470.cfg'), 'w')
#  f_trc_cfg.write(txt)
#  flush_and_close( f_trc_cfg )
#  
#  # ##############################################################
#  # S T A R T   T R A C E   i n   S E P A R A T E    P R O C E S S
#  # ##############################################################
#  
#  f_trc_log=open( os.path.join(context['temp_directory'],'tmp_trc_5470.log'), "w")
#  f_trc_err=open( os.path.join(context['temp_directory'],'tmp_trc_5470.err'), "w")
#  
#  p_trace = Popen( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_start' , 'trc_cfg', f_trc_cfg.name],stdout=f_trc_log,stderr=f_trc_err)
#  
#  time.sleep(1)
#  
#  # ####################################################
#  # G E T  A C T I V E   T R A C E   S E S S I O N   I D
#  # ####################################################
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  
#  f_trc_lst = open( os.path.join(context['temp_directory'],'tmp_trace_5470.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_list'], stdout=f_trc_lst)
#  flush_and_close( f_trc_lst )
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
#  ddl_lst=(
#      '''recreate		
#  
#      	table		
#  
#  
#  
#      	t_test(x int)	
#      ''',
#      '''comment on		
#      table			
#  
#  
#      t_test is			
#      	'foo
#      	bar'	
#      ''',
#      '''
#  
#      	create
#      or
#  
#      alter
#      		view
#  
#      		v_rio
#  
#      		as
#      		select *
#      		from
#  
#      		rdb$database
#      '''
#  )
#  
#  con1 = fdb.connect(dsn=dsn)
#  for s in ddl_lst:
#    con1.execute_immediate(s)
#  
#  con1.commit()
#  con1.close()
#  
#  # Let trace log to be entirely written on disk:
#  time.sleep(2)
#  
#  # ####################################################
#  # S E N D   R E Q U E S T    T R A C E   T O   S T O P
#  # ####################################################
#  if trcssn>0:
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_stop','trc_id', trcssn], stdout=fn_nul)
#      fn_nul.close()
#  #    # DO NOT REMOVE THIS LINE:
#  #    time.sleep(2)
#  
#  p_trace.terminate()
#  flush_and_close( f_trc_log )
#  flush_and_close( f_trc_err )
#  
#  # Following file should be EMPTY:
#  ################
#  
#  f_list=(f_trc_err,)
#  for i in range(len(f_list)):
#      f_name=f_list[i].name
#      if os.path.getsize(f_name) > 0:
#          with open( f_name,'r') as f:
#              for line in f:
#                  print("Unexpected STDERR, file "+f_name+": "+line)
#  
#  with open( f_trc_log.name,'r') as f:
#      lines=f.read()
#      for s in ddl_lst:
#          print( 'FOUND' if lines.find(s) > 0 else 'NOT found' )
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( (f_trc_cfg, f_trc_lst, f_trc_log, f_trc_err) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    FOUND
    FOUND
    FOUND
  """

@pytest.mark.version('>=2.5.7')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


