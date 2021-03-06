#coding:utf-8
#
# id:           bugs.core_4977
# title:        Detach using Linux client takes much longer than from Windows
# decription:   
#                   # *** NOTE ***
#                   # We measure APPROXIMATE time that is required for detaching from database by evaluating number of seconds that passed
#                   # from UNIX standard epoch time inside ISQL and writing it to log. After returning control from ISQL we evaluate again
#                   # that number by calling Python 'time.time()' - and it will return value upto current UTC time, i.e. it WILL take in
#                   # account local timezone from OS settings (this is so at least on Windows). Thus we have to add/substract time shift
#                   # between UTC and local time - this is done by 'time.timezone' summand.
#                   # On PC-host with CPU 3.0 GHz and 2Gb RAM) in almost all cases difference was less than 1000 ms, so it was decided 
#                   # to set MAX_DETACH_TIME_THRESHOLD = 1200 ms.
#                   # Tested on WI-V3.0.0.32140 (SS/SC/CC).
#               
#                   Results for 22.05.2017:
#                       fb30Cs, build 3.0.3.32725: OK, 1.796ss.
#                       fb30SC, build 3.0.3.32725: OK, 1.047ss.
#                       FB30SS, build 3.0.3.32725: OK, 0.937ss.
#                       FB40CS, build 4.0.0.645: OK, 2.032ss.
#                       FB40SC, build 4.0.0.645: OK, 1.188ss.
#                       FB40SS, build 4.0.0.645: OK, 1.157ss.
#               
#                   13.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 3.0.8.33445, 4.0.0.2416
#                     Linux:   3.0.8.33426, 4.0.0.2416
#                
# tracker_id:   CORE-4977
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
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
#  db_conn.close()
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  ############################################
#  ###   d e f i n e    t h r e s h o l d   ###
#  ############################################
#  MAX_DETACH_TIME_THRESHOLD=1200
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
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  sqltxt='''
#      set list on; 
#      select datediff(second from timestamp '01.01.1970 00:00:00.000' to current_timestamp) as " " 
#      from rdb$types rows 1;
#  '''
#  
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_4977.sql'), 'w')
#  f_isql_cmd.write(sqltxt)
#  flush_and_close( f_isql_cmd )
#  
#  ms_before_detach=0
#  
#  f_isql_log = open( os.path.join(context['temp_directory'],'tmp_4977.log'), 'w')
#  f_isql_err = open( os.path.join(context['temp_directory'],'tmp_4977.err'), 'w')
#  
#  subprocess.call( [context['isql_path'], dsn, "-i", f_isql_cmd.name ],
#                   stdout = f_isql_log,
#                   stderr = f_isql_err
#                 )
#  flush_and_close( f_isql_log )
#  flush_and_close( f_isql_err )
#  
#  with open( f_isql_log.name,'r') as f:
#      for line in f:
#          # ::: NB  ::: do NOT remove "and line.split()[0].isdigit()" if decide to replace subprocess.call()
#          # with pipe-way like: runProgram('isql',[dsn,'-q','-o',sqllog.name], sqltxt) !!
#          # String like: 'Database ....' does appear first in log instead of result!
#          if line.split() and line.split()[0].isdigit():
#              ms_before_detach=int( line.split()[0] )
#  
#  detach_during_ms = int( (time.time() - ms_before_detach  - time.timezone) * 1000 )
#  
#  if detach_during_ms < MAX_DETACH_TIME_THRESHOLD:
#      print('Detach performed fast enough: less than threshold.')
#  else:
#      print('Detach lasted too long time: %s ms, MAX_DETACH_TIME_THRESHOLD is %s ms' % (detach_during_ms, MAX_DETACH_TIME_THRESHOLD) )
#  
#  # cleanup:
#  time.sleep(1)
#  cleanup((f_isql_log, f_isql_err, f_isql_cmd))
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Detach performed fast enough: less than threshold.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


