#coding:utf-8
#
# id:           bugs.core_4398
# title:        Provide ability to specify extra-long name of log when doing gbak to avoid "attempt to store 256 bytes in a clumplet" message
# decription:   
# tracker_id:   CORE-4398
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  
#  print ('Starting backup...')
#  fbk = os.path.join(context['temp_directory'],'backup.fbk')
#  lbk = os.path.join(context['temp_directory'],'A012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890.log')
#  fdn = 'localhost:'+os.path.join(context['temp_directory'],'tmp4398.tmp')
#  #runProgram('gbak',['-b','-se','localhost:service_mgr','-v','-y',lbk, '-user',user_name,'-password',user_password,dsn,fbk])
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,'-v','-y',lbk,dsn,fbk])
#  print ('Backup finished.')
#  if os.path.isfile(fbk):
#      print ('Delete backup file...')
#      os.remove(fbk)
#      print ('Backup file deleted.')
#      print ('Delete log file...')
#      os.remove(lbk)
#      print ('Log file deleted.')
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Starting backup...
    Backup finished.
    Delete backup file...
    Backup file deleted.
    Delete log file...
    Log file deleted.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


