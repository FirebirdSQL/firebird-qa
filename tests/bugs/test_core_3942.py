#coding:utf-8
#
# id:           bugs.core_3942
# title:        Restore from gbak backup using service doesn't report an error
# decription:   
#                    Checked on:
#                      WI-V2.5.6.26994 SC
#                      WI-V3.0.0.32474 SS/SC/CS
#                      LI-T4.0.0.130 // 11.04.2016
#                      WI-T4.0.0.132 // 12.04.2016
#                
# tracker_id:   CORE-3942
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('gbak: ERROR:.*database.*already exists.*', 'gbak: ERROR:database already exists.*'), ('database.*already exists.*', ''), ('-Exiting before completion due to errors', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  db_conn.close()
#  fdb='$(DATABASE_LOCATION)bugs.core_3942.fdb'
#  fbk = os.path.join(context['temp_directory'],'tmp.core_3942.fbk')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  print ('Trying to overwrite existing database file using gbak -se...')
#  runProgram('gbak',['-c','-se','localhost:service_mgr','-user',user_name,'-password',user_password,fbk,fdb])
#  print ('Trying to overwrite existing database file using fbsvcmgr...')
#  runProgram('fbsvcmgr',['localhost:service_mgr','user','SYSDBA','password','masterkey','action_restore','dbname',fdb,'bkp_file',fbk])
#  if os.path.isfile(fbk):
#      os.remove(fbk)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Trying to overwrite existing database file using gbak -se...
    Trying to overwrite existing database file using fbsvcmgr...
  """
expected_stderr_1 = """
    gbak: ERROR:database C:/FBTESTING/qa/fbt-repo/tmp/bugs.core_3942.fdb already exists.  To replace it, use the -REP switch
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors
    database C:/FBTESTING/qa/fbt-repo/tmp/bugs.core_3942.fdb already exists.  To replace it, use the -REP switch

  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_core_3942_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


