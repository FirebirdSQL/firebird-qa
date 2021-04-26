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
#                   # to set threshold = 1200 ms.
#                   # Tested on WI-V3.0.0.32140 (SS/SC/CC).
#                   ##########################################################################
#                   # Test on LINUX was not done yet, so I've assign platform = 'Windows' yet.
#                   ##########################################################################
#                   Results for 22.05.2017:
#                       fb30Cs, build 3.0.3.32725: OK, 1.796ss.
#                       fb30SC, build 3.0.3.32725: OK, 1.047ss.
#                       FB30SS, build 3.0.3.32725: OK, 0.937ss.
#                       FB40CS, build 4.0.0.645: OK, 2.032ss.
#                       FB40SC, build 4.0.0.645: OK, 1.188ss.
#                       FB40SS, build 4.0.0.645: OK, 1.157ss.
#               
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
#  sqltxt='''
#      set list on; 
#      select datediff(second from timestamp '01.01.1970 00:00:00.000' to current_timestamp) as " " 
#      from rdb$types rows 1;
#  '''
#  
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_4977.sql'), 'w')
#  f_isql_cmd.write(sqltxt)
#  f_isql_cmd.close()
#  
#  ms_before_detach=0
#  
#  f_isql_log = open( os.path.join(context['temp_directory'],'tmp_4977.log'), 'w')
#  f_isql_err = open( os.path.join(context['temp_directory'],'tmp_4977.err'), 'w')
#  
#  subprocess.call( ["isql", dsn, "-i", f_isql_cmd.name ],
#                   stdout = f_isql_log,
#                   stderr = f_isql_err
#                 )
#  f_isql_log.close()
#  f_isql_err.close()
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
#  ############################################
#  ###   d e f i n e    t h r e s h o l d   ###
#  ############################################
#  threshold=1200
#  
#  if detach_during_ms < threshold:
#      print('Detach performed fast enough: less than threshold.')
#  else:
#      print('Detach lasted too long time: %s ms, threshold is %s ms' % (detach_during_ms, threshold) )
#  
#  f_list=(f_isql_log, f_isql_err, f_isql_cmd)
#  for i in range(len(f_list)):
#     if os.path.isfile(f_list[i].name):
#         os.remove(f_list[i].name)
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Detach performed fast enough: less than threshold.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_4977_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


