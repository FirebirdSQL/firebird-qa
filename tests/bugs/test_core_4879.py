#coding:utf-8
#
# id:           bugs.core_4879
# title:        Minor inconvenience in user management via services API
# decription:   
#                   Confirmed weird error message on 3.0.0.31374.
#                   Command:
#                       fbsvcmgr.exe localhost:service_mgr user sysdba password masterkey action_add_user dbname employee sec_username foo sec_password 123
#                   - failed with:
#                       unexpected item in service parameter block, expected isc_spb_sec_username
#                   Checked on 4.0.0.2307; 3.0.8.33393.
#                
# tracker_id:   CORE-4879
# min_versions: ['3.0.0']
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
# import os
#  import subprocess
#  from subprocess import Popen
#  import time
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
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_fdb=db_conn.database_name
#  db_conn.close()
#  
#  f_svc_log=open( os.path.join(context['temp_directory'],'tmp_4879_fbsvc.log'), "w", buffering = 0)
#  # C:\\FB\\old.3b1
#  bsvcmgr.exe localhost:service_mgr user sysdba password masterkey action_add_user dbname employee sec_username foo sec_password 123
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr", "action_add_user", "dbname",  this_fdb, "sec_username", "TMP$C4879", "sec_password", "123" ],
#                   stdout=f_svc_log,
#                   stderr=subprocess.STDOUT
#                 )
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr", "action_delete_user", "dbname",  this_fdb, "sec_username", "TMP$C4879" ],
#                   stdout=f_svc_log,
#                   stderr=subprocess.STDOUT
#                 )
#  
#  flush_and_close(f_svc_log)
#  
#  with open( f_svc_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED OUTPUT in '+f_svc_log.name+': '+line)
#  
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( (f_svc_log.name,) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_4879_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


