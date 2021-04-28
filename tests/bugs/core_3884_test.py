#coding:utf-8
#
# id:           bugs.core_3884
# title:        Server crashes on preparing empty query when trace is enabled
# decription:   
#                  Could reproduce crash only once. All other attempts were useless - FB lives.
#                
# tracker_id:   CORE-3884
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('Unexpected end of command.*', 'Unexpected end of command')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import re
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
#  db_file = db_conn.database_name
#  # do NOT: db_conn.close()
#  
#  #---------------------------------------------
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
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  txt25 = '''# Trace config, format for 2.5. Generated auto, do not edit!
#  <database %[\\\\\\\\/]bugs.core_3884.fdb>
#    enabled true
#    time_threshold 0
#    log_statement_prepare true
#    # exclude_filter '%execute block%'
#    # did not work in 2.5.1: include_filter '%(INSERT|UPDATE|DELETE|SELECT)%'
#    log_statement_finish true
#  </database>
#  '''
#  
#  # NOTES ABOUT TRACE CONFIG FOR 3.0:
#  # 1) Header contains `database` clause in different format vs FB 2.5: its data must be enclosed with '{' '}'
#  # 2) Name and value must be separated by EQUALITY sign ('=') in FB-3 trace.conf, otherwise we get runtime error:
#  #    element "<. . .>" have no attribute value set
#  
#  txt30 = '''# Trace config, format for 3.0. Generated auto, do not edit!
#  database=%[\\\\\\\\/]bugs.core_3884.fdb
#  {
#    enabled = true
#    time_threshold = 0
#    log_statement_finish = true
#  }
#  '''
#  
#  f_trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trace_3884.cfg'), 'w')
#  if engine.startswith('2.5'):
#      f_trc_cfg.write(txt25)
#  else:
#      f_trc_cfg.write(txt30)
#  f_trc_cfg.close()
#  
#  # ##############################################################
#  # S T A R T   T R A C E   i n   S E P A R A T E    P R O C E S S
#  # ##############################################################
#  
#  f_trc_log=open( os.path.join(context['temp_directory'],'tmp_trace_3884.log'), "w")
#  f_trc_err=open( os.path.join(context['temp_directory'],'tmp_trace_3884.err'), "w")
#  
#  p_trace = Popen( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_start' , 'trc_cfg', f_trc_cfg.name],stdout=f_trc_log,stderr=f_trc_err)
#  
#  # this delay need for trace start and finish its output about invalid section in its config file:
#  time.sleep(2)
#  
#  # ####################################################
#  # G E T  A C T I V E   T R A C E   S E S S I O N   I D
#  # ####################################################
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  
#  f_trc_lst = open( os.path.join(context['temp_directory'],'tmp_trace_3884.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_list'], stdout=f_trc_lst)
#  flush_and_close( f_trc_lst )
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
#  
#  # Result: `trcssn` is ID of active trace session. Now we have to terminate it:
#  
#  
#  #.............................................................................
#  
#  sql_cmd='''    execute block returns(n int) as
#          declare s varchar(100) = 'SELECT count(*) from rdb$database';
#      begin
#          execute statement s into n;
#          suspend;
#      end
#  '''
#  
#  #sql_cmd='	\\n	\\n\\n	'
#  sql_cmd=''
#  
#  cur=db_conn.cursor()
#  try:
#      cur.execute( sql_cmd )
#      for r in cur:
#           n = r[0]
#  except Exception,e:
#      for i in e[0].split('\\n'):
#          print('error text:',i)
#  finally:
#      cur.close()
#  
#  db_conn.commit()
#  #.............................................................................
#  
#  
#  # ####################################################
#  # S E N D   R E Q U E S T    T R A C E   T O   S T O P
#  # ####################################################
#  if trcssn>0:
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_stop','trc_id', trcssn], stdout=fn_nul)
#      fn_nul.close()
#      # DO NOT REMOVE THIS LINE:
#      time.sleep(2)
#  
#  
#  p_trace.terminate()
#  flush_and_close( f_trc_log )
#  flush_and_close( f_trc_err )
#  
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_trc_cfg, f_trc_log, f_trc_err, f_trc_lst) ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    error text: Error while preparing SQL statement:
    error text: - SQLCODE: -104
    error text: - Unexpected end of command - line 1, column 1
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


