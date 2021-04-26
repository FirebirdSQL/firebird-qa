#coding:utf-8
#
# id:           bugs.core_3188
# title:        page 0 is of wrong type (expected 6, found 1)
# decription:   
#                  Confirmed on WI-V2.5.0.26074
#                    exception:
#                    DatabaseError:
#                    Error while commiting transaction:
#                    - SQLCODE: -902
#                    - database file appears corrupt (C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\BUGS.CORE_3188.FDB)
#                    - wrong page type
#                    - page 0 is of wrong type (expected 6, found 1)
#                    -902
#                    335544335
#               
#                  New messages in firebird.log in 2.5.0 after running ticket statements:
#               
#                   CSPROG (Client)	Mon Feb 15 07:28:05 2016
#                       INET/inet_error: connect errno = 10061
#                   CSPROG	Mon Feb 15 07:41:02 2016
#                       Shutting down the server with 0 active connection(s) to 0 database(s), 1 active service(s)
#                
# tracker_id:   CORE-3188
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import difflib
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  engine = str(db_conn.engine_version)
#  db_conn.close()
#  
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
#    # ::: NB ::: Service call for receive firebird.log works properly only since FB 2.5.2!
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
#                    stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  #--------------------------------------------
#  
#  
#  # Start two attachments:
#  con1 = kdb.connect(dsn=dsn)
#  con2 = kdb.connect(dsn=dsn)
#  
#  # Session-1:
#  c1 = con1.cursor()
#  
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_3188_fblog_before.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  c1.execute("create table test(id int primary key)")
#  con1.commit()
#  
#  # Session-2:
#  
#  c2 = con2.cursor()
#  c2.execute('drop table test')
#  con2.commit()
#  
#  # cleanup
#  con1.close()
#  con2.close()
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_3188_fblog_after.txt'), 'w')
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_3188_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  # Difference of firebird.log should be EMPTY:
#  
#  with open( f_diff_txt.name,'r') as f:
#      print( f.read() )
#  f.close()
#  
#  ###############################
#  # Cleanup.
#  cleanup( [i.name for i in (f_fblog_before, f_fblog_after, f_diff_txt)] )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.1')
@pytest.mark.xfail
def test_core_3188_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


