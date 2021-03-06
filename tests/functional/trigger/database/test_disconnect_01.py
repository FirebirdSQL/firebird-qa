#coding:utf-8
#
# id:           functional.trigger.database.disconnect_01
# title:        Trigger on database disconnect: check that exception that raised when trigger fires is written to firebird.log
# decription:   
#                   Discussed with Alex, 16.12.2020 functionality that was not specified in the documentation:
#                   exception that raises in a trigger on DISCONNECT reflects in the firebird.log.
#               
#                   Test creates trigger on disconnect and put in its body statement which always will fail: 1/0.
#                   Then we get content of firebird.log before disconnect and after.
#                   Finally we compare these logs and search in the difference lines about error message.
#               
#                   Checked on 4.0.0.2303 SS/CS.
#                 
# tracker_id:   
# min_versions: []
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
    set term ^;
    create trigger trg_disconnect on disconnect as
        declare n int;
    begin
        n = 1/0;
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import difflib
#  import re
#  import time
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
#  def svc_get_fb_log( fb_home, f_fb_log ):
#  
#    global subprocess
#    subprocess.call( [ context['fbsvcmgr_path'],
#                       "localhost:service_mgr",
#                       "action_get_fb_log"
#                     ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  #--------------------------------------------
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  f_init_log = open( os.path.join(context['temp_directory'],'tmp_fb_old.log'), 'w')
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr",  "action_get_fb_log" ], stdout = f_init_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_init_log )
#  
#  db_conn.close() # this leads to zero divide error in trg_disconnect which must be reflected in the firebird.log
#  
#  time.sleep(1)
#  
#  f_curr_log = open( os.path.join(context['temp_directory'],'tmp_fb_new.log'), 'w')
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr",  "action_get_fb_log" ], stdout = f_curr_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_curr_log )
#  
#  f_init_log=open(f_init_log.name, 'r')
#  f_curr_log=open(f_curr_log.name, 'r')
#  difftext = ''.join(difflib.unified_diff(
#      f_init_log.readlines(), 
#      f_curr_log.readlines()
#    ))
#  flush_and_close( f_init_log )
#  flush_and_close( f_curr_log )
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_fb_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  p = re.compile('\\+\\s?((Error at disconnect)|(arithmetic exception)|(Integer divide by zero)|(At trigger))')
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and line.strip() != '+++' and p.search(line):
#              print( line )
#              # print( 'DIFF in firebird.log: %(line)s' % locals() )
#  
#  ###############################
#  # Cleanup.
#  time.sleep(1)
#  cleanup( (f_init_log,f_curr_log,f_diff_txt) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    + Error at disconnect:
    + arithmetic exception, numeric overflow, or string truncation
    + Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
    + At trigger 'TRG_DISCONNECT' line: 4, col: 9
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


