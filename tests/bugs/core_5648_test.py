#coding:utf-8
#
# id:           bugs.core_5648
# title:        Avoid serialization of isc_attach_database calls issued by EXECUTE STATEMENT implementation
# decription:   
#                   We use special IP = 192.0.2.2 as never reachable address thus any attempt to connect it will fail.
#                   Currently FB tries to establish connect to this host about 20-22 seconds.
#                   We launch 1st ISQL in Async mode (using subprocess.Popen) with task to establish connect to this host.
#                   At the same time we launch 2nd ISQL with EDS to localhost and the same DB as test uses.
#                   Second ISQL must do its job instantly, despite of hanging 1st ISQl, and time for this is about 50 ms.
#                   We use threshold and compare time for which 2nd ISQL did its job. Finally, we ouptput result of this comparison.
#               
#                   ::::::::::::: NOTE :::::::::::::::::::
#                   As of current FB snapshots, there is NOT ability to interrupt ISQL which tries to make connect to 192.0.2.2,
#                   until this ISQL __itself__ make decision that host is unreachable. This takes about 20-22 seconds.
#                   Also, if we kill this (hanging) ISQL process, than we will not be able to drop database until this time exceed.
#                   For this reason, it was decided not only to kill ISQL but also run fbsvcmgr with DB full-shutdown command - this
#                   will ensure that database is really free from any attachments and can be dropped.
#               
#                   :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#                   See also http://tracker.firebirdsql.org/browse/CORE-5609
#                   :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#               
#               
#                   Reproduced bug on 3.0.3.32756 (SC, 15-jul-2017), 4.0.0.690 (SC, 15-jul-2017)
#                   Passed on:
#                       3.0.3.32805: OK, 24.797s (Classic, 21-sep-2017)
#                       3.0.3.32828: OK, 25.328s (SuperServer, 08-nov-2017)
#                       4.0.0.748: OK, 25.984s (Classic)
#                       4.0.0.789: OK, 24.406s (SuperClassic and SuperServer, 08-nov-2017).
#                
# tracker_id:   CORE-5648
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
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
#  import difflib
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file = db_conn.database_name
#  
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
#  usr=user_name
#  pwd=user_password
#  remote_host = '192.0.2.2'
#  
#  eds_query='''
#      set bail on;
#      set list on;
#      --select current_timestamp as " " from rdb$database;
#      set term ^;
#      execute block as
#          declare c smallint;
#          declare remote_host varchar(50) = '%(remote_host)s'; -- never unreachable: 192.0.2.2
#      begin
#          rdb$set_context('USER_SESSION','DTS_BEG', cast('now' as timestamp) );
#          execute statement 'select 1 from rdb$database'
#          on external remote_host || ':' || rdb$get_context('SYSTEM', 'DB_NAME')
#          as user '%(usr)s' password '%(pwd)s'
#          into c;
#      end
#      ^
#      set term ;^
#      --select current_timestamp as " " from rdb$database; 
#      select iif( waited_ms < max_wait_ms, 
#                  'OK: second EDS was fast', 
#                  'FAILED: second EDS waited too long, ' || waited_ms || ' ms - more than max_wait_ms='||max_wait_ms 
#                ) as result_msg
#      from (
#          select 
#              datediff( millisecond from cast( rdb$get_context('USER_SESSION','DTS_BEG') as timestamp) to current_timestamp ) as waited_ms
#             ,500 as max_wait_ms
#          --   ^
#          --   |                                  #################
#          --   +--------------------------------  T H R E S H O L D
#          --                                      #################
#          from rdb$database
#      );
#  '''
#  
#  f_eds_to_unavail_host_sql = open( os.path.join(context['temp_directory'],'tmp_unavail_host_5648.sql'), 'w')
#  f_eds_to_unavail_host_sql.write( eds_query % locals() )
#  flush_and_close( f_eds_to_unavail_host_sql )
#  
#  remote_host = 'localhost'
#  f_eds_to_local_host_sql = open( os.path.join(context['temp_directory'],'tmp_local_host_5648.sql'), 'w')
#  f_eds_to_local_host_sql.write( eds_query % locals() )
#  flush_and_close( f_eds_to_local_host_sql )
#  
#  
#  
#  f_eds_to_unavail_host_log = open( os.path.join(context['temp_directory'],'tmp_unavail_host_5648.log'), 'w')
#  f_eds_to_unavail_host_err = open( os.path.join(context['temp_directory'],'tmp_unavail_host_5648.err'), 'w')
#  p_isql_to_unavail_host=subprocess.Popen( [context['isql_path'], dsn, "-n", "-i", f_eds_to_unavail_host_sql.name ],
#                   stdout = f_eds_to_unavail_host_log,
#                   stderr = f_eds_to_unavail_host_err
#                 )
#  
#  # Let ISQL be loaded:
#  time.sleep(1)
#  
#  f_eds_to_local_host_log = open( os.path.join(context['temp_directory'],'tmp_local_host_5648.log'), 'w')
#  f_eds_to_local_host_err = open( os.path.join(context['temp_directory'],'tmp_local_host_5648.err'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-n", "-i", f_eds_to_local_host_sql.name ],
#                   stdout = f_eds_to_local_host_log,
#                   stderr = f_eds_to_local_host_err
#                 )
#  
#  #............ kill ISQL that is attampting to found 192.0.2.2 host and thus will hang for about 45 seconds .......
#  
#  p_isql_to_unavail_host.terminate()
#  flush_and_close( f_eds_to_unavail_host_log )
#  flush_and_close( f_eds_to_unavail_host_err )
#  
#  flush_and_close( f_eds_to_local_host_log )
#  flush_and_close( f_eds_to_local_host_err )
#  
#  # Make DB shutdown and bring online because some internal server process still can be active!
#  # If we skip this step than runtime error related to dropping test DB can occur!
#  #########################################
#  
#  f_db_reset_log=open( os.path.join(context['temp_directory'],'tmp_reset_5648.log'), 'w')
#  f_db_reset_err=open( os.path.join(context['temp_directory'],'tmp_reset_5648.err'), 'w')
#  
#  f_db_reset_log.write('Point before DB shutdown.'+os.linesep)
#  f_db_reset_log.seek(0,2)
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_shutdown_mode", "prp_sm_full", "prp_shutdown_db", "0",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_db_reset_log,
#                   stderr = f_db_reset_err
#                 )
#  f_db_reset_log.write(os.linesep+'Point after DB shutdown.'+os.linesep)
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_db_online",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_db_reset_log,
#                   stderr = f_db_reset_err
#                 )
#  
#  f_db_reset_log.write(os.linesep+'Point after DB online.'+os.linesep)
#  flush_and_close( f_db_reset_log )
#  flush_and_close( f_db_reset_err )
#  
#  with open( f_eds_to_local_host_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('STDLOG of 2nd EDS: ', ' '.join(line.split()) )
#  
#  
#  with open( f_eds_to_local_host_err.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED STDERR in '+f_eds_to_local_host_err.name+': '+line)
#  
#  with open( f_db_reset_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('STDLOG of DB reset: ', ' '.join(line.split()) )
#  
#  with open( f_db_reset_err.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED STDERR in '+f_db_reset_log.name+': '+line)
#  
#  ###############################
#  # Cleanup.
#  time.sleep(1)
#  
#  f_list=( 
#       f_eds_to_local_host_sql 
#      ,f_eds_to_local_host_log 
#      ,f_eds_to_local_host_err 
#      ,f_eds_to_unavail_host_sql 
#      ,f_eds_to_unavail_host_log 
#      ,f_eds_to_unavail_host_err
#      ,f_db_reset_log 
#      ,f_db_reset_err 
#  )
#  cleanup( f_list )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STDLOG of 2nd EDS:  RESULT_MSG OK: second EDS was fast
    STDLOG of DB reset:  Point before DB shutdown.
    STDLOG of DB reset:  Point after DB shutdown.
    STDLOG of DB reset:  Point after DB online.
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


