#coding:utf-8
#
# id:           bugs.core_6509
# title:        Segfault when gfix requests for database page buffer more memory than available from OS
# decription:   
#                   Confirmed crash on 4.0.0.2377 (Windows and Linux)
#                   Checked on 4.0.0.2384 - all OK, get STDERR: "unable to allocate memory from operating system"
#                   NB: currently acceptable value for '-buffers' is limited from 50 to 2147483646.
#                
# tracker_id:   CORE-6509
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=32768, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import re
#  import time
#  
#  so=sys.stdout
#  se=sys.stderr
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_name = db_conn.database_name
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
#  
#  f_log = open( os.path.join(context['temp_directory'],'tmp_c6509.log'), 'w')
#  f_err = open( os.path.join(context['temp_directory'],'tmp_c6509.err'), 'w')
#  sys.stdout = f_log
#  sys.stderr = f_err
#  
#  runProgram('gstat',[ '-h', db_name ])
#  runProgram('gfix',[dsn,'-buffers','2147483646'])
#  runProgram('gstat',[ '-h', db_name ])
#  
#  sys.stdout = so
#  sys.stderr = se
#  
#  flush_and_close( f_log )
#  flush_and_close( f_err )
#  
#  pattern_for_page_buffers = re.compile('\\s*Page\\s+buffers\\s+\\d+', re.IGNORECASE)
#  
#  buffers_set=set()
#  with open(f_log.name,'r') as f:
#      for line in f:
#          if pattern_for_page_buffers.search(line):
#              buffers_set.add( line.split()[2] )
#              # print('gstat output:', line)
#  
#  print( 'Buffers value was ' + ('not changed (expected)' if len(buffers_set) == 1 else 'UNEXPECTEDLY changed: ' + (', '.join(buffers_set)) ) )
#  
#  with open(f_err.name,'r') as f:
#      for line in f:
#          print('STDERR in gfix:', line)
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_log,f_err) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Buffers value was not changed (expected)
    STDERR in gfix: unable to allocate memory from operating system
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


