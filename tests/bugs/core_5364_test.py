#coding:utf-8
#
# id:           bugs.core_5364
# title:        gfix -online normal <db> (being issued in window #1) does not produce error when there is sysdba attachment in window #2
# decription:   
#                   We create new DB and immediately change its state to single-user maintanance.
#                   Then we attach to this DB ans run (in separate process) 'gfix -online normal <localhost:this_db>'.
#                   This command must produce in its STDERR error: "database ... shutdown" - and we check that this actually occurs.
#                   Also, we check that after reconnect to this DB value of mon$database.mon$shutdown_mode remains the same: 2.
#               
#                   Confirmed bug on: 4.0.0.1850 SS, 3.0.6.33276 SS - no error when doing 'gfix -online normal'.
#                   Checked on 4.0.0.1881 SS, 3.0.6.33283 SS -- all fine, DB state is not changed to normal.
#                
# tracker_id:   CORE-5364
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('database .* shutdown', 'database shutdown')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
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
#  tmpfdb = os.path.join( context['temp_directory'], 'tmp_5364.fdb')
#  cleanup( (tmpfdb,) )
#  
#  con1=fdb.create_database(dsn = 'localhost:' + tmpfdb)
#  con1.close()
#  subprocess.call( [ context['gfix_path'], 'localhost:' + tmpfdb, '-shut', 'single', '-force', '0'] )
#  
#  con1=fdb.connect(dsn = 'localhost:' + tmpfdb)
#  
#  f_gfix_online_log=open( os.path.join(context['temp_directory'],'tmp_5364_online.log'), 'w', buffering = 0)
#  f_gfix_online_err=open( os.path.join(context['temp_directory'],'tmp_5364_online.err'), 'w', buffering = 0)
#  
#  subprocess.call( [ context['gfix_path'], 'localhost:' + tmpfdb, '-online', 'normal'], stdout=f_gfix_online_log, stderr=f_gfix_online_err )
#  
#  flush_and_close( f_gfix_online_log )
#  flush_and_close( f_gfix_online_err )
#  
#  con1.close()
#  
#  con1=fdb.connect(dsn = 'localhost:' + tmpfdb)
#  cur1=con1.cursor()
#  cur1.execute('select d.mon$shutdown_mode from mon$database d')
#  for r in cur1:
#      print( 'DB shutdown mode:', r[0] )
#  cur1.close()
#  con1.close()
#  
#  with open(f_gfix_online_err.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print(line)
#  
#  # cleanup
#  ##########
#  time.sleep(1)
#  cleanup( (f_gfix_online_log, f_gfix_online_err, tmpfdb) )
#  
#  # database C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\TMP_5364.FDB shutdown
#  # database /opt/scripts/qa-rundaily/fbt-repo/tmp/tmp_5364.fdb shutdown
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DB shutdown mode: 2
    database C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\TMP_5364.FDB shutdown
  """

@pytest.mark.version('>=3.0.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


