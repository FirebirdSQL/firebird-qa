#coding:utf-8
#
# id:           bugs.core_3732
# title:        Segfault when closing attachment to database
# decription:   
#                  Confirmed bug on: WI-V2.5.1.26351. Works fine on WI-V2.5.2.26540
#                  On 2.5.1:
#                  1) test finished with:
#                    ERROR: bugs.core_3732
#                    Test cleanup: Exception raised while dropping database.
#                    FAILED (errors=1)
#                  2) firebird.log did contain:
#                    REMOTE INTERFACE/gds__detach: Unsuccesful detach from database. 
#                    Uncommitted work may have been lost
#                
# tracker_id:   CORE-3732
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = [('STATEMENT FAILED, SQLSTATE = HY000', ''), ('RECORD NOT FOUND FOR USER: TMP\\$C3732', ''), ('AFTER LINE.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import subprocess
#  import time
#  import difflib
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
#  db_file = db_conn.database_name
#  db_conn.close()
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
#  def svc_get_fb_log( engine, f_fb_log ):
#  
#    import subprocess
#  
#    if engine.startswith('2.5'):
#        get_firebird_log_key='action_get_ib_log'
#    else:
#        get_firebird_log_key='action_get_fb_log'
#  
#    subprocess.call([ context['fbsvcmgr_path'],
#                      "localhost:service_mgr",
#                      get_firebird_log_key
#                    ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#  
#    return
#  
#  #--------------------------------------------
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_3732_fblog_before.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  sql_ddl='''
#      drop user tmp$c3732;
#      commit;
#      create role REPL_ADMIN;
#      create user tmp$c3732 password '12345';
#      grant repl_admin to tmp$c3732;
#      revoke all on all from tmp$c3732;
#      drop user tmp$c3732;
#      exit; 
#  '''
#  
#  f_ddl_sql = open( os.path.join(context['temp_directory'],'tmp_ddl_3732.sql'), 'w')
#  f_ddl_sql.write(sql_ddl)
#  flush_and_close( f_ddl_sql )
#  
#  f_ddl_log = open( os.path.join(context['temp_directory'],'tmp_ddl_3732.log'), 'w')
#  subprocess.call( [ context['isql_path'], dsn, "-q", "-i",f_ddl_sql.name ],
#                   stdout=f_ddl_log,
#                   stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_ddl_log )
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_3732_fblog_after.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  # Now we can compare two versions of firebird.log and check their difference.
#  
#  oldfb=open(f_fblog_before.name, 'r')
#  newfb=open(f_fblog_after.name, 'r')
#  
#  difftext = ''.join(difflib.unified_diff(
#      oldfb.readlines(), 
#      newfb.readlines()
#    ))
#  oldfb.close()
#  newfb.close()
#  
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_3732_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  # This should be empty:
#  #######################
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          print( line.upper() )
#  
#  # This should be empty:
#  #######################
#  with open( f_ddl_log.name,'r') as f:
#      for line in f:
#          print(line.upper())
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_fblog_before, f_ddl_sql, f_ddl_log, f_fblog_after, f_diff_txt) ] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.2')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


