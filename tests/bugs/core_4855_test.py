#coding:utf-8
#
# id:           bugs.core_4855
# title:        Online validation during DML activity in other connection leads to message "Error while trying to read from file" and "page in use during flush (210), file: cch.cpp line: 2672"
# decription:   
#                  In order to check ticket issues this test does following:
#                  1. Change on test database FW to OFF - this will increase DML performance.
#                  2. Create two tables: one for inserting rows ('test') and second to serve as 'signal' to stop DML:
#                     inserts will be done until 2nd table (with name = 'stop') is empty.
#                  3. Adds to SQL script DML (execute block) that will be used in ISQL session #1: it inserts rows 
#                     into 'test' and checks after each inserting table 'stop' on presence there at least one row. 
#                     This 'stop-row' will be inserted into 'stop' table in another ISQL session.
#                  4. Launches ISQL connection #1 in separate (child) process. This ISQL will start 'heavy DML'.
#                  5. Proceeds several online-validation actions by using synchronous call of 'FBSVCMGR action_validate'.
#                     Adds result of each validation to log.
#                  6. Launches ISQL connection #2 in separate (child) process and give to this session trivial job:
#                     'insert into stop(id) values(1); commit;'. This will cause ISQL session #1 to stop its activity 
#                     because it runs in transaction with TIL = RC.
#                  7. Outputs log of ISQL-1 and online validation results.
#               
#                  Tested on WI-V3.0.0.32008, SS, SC and CS. Result: OK.
#                  Updated since WI-V3.0.0.32064: reduced key-length from extremely huge (1000) to "normal" value 36, 
#                  otherwise get 'Statement failed, SQLSTATE = 54000 / Implementation limit exceeded / -Maximum index level reached'.
#                  (since CORE-4914 was fixed, see:  http://sourceforge.net/p/firebird/code/62266 )
#                
# tracker_id:   CORE-4855
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]', ''), ('Relation [0-9]{3,4}', 'Relation'), ('Statement failed, SQLSTATE = HY008', ''), ('operation was cancelled', ''), ('After line .*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  
#  import os
#  import subprocess
#  from subprocess import Popen
#  #import signal
#  import time
#  from fdb import services
#  
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
#  dbname=db_conn.database_name
#  db_conn.close()
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
#  #####################################################################
#  # Change database FW to OFF in order to increase speed of insertions and output its header info:
#  
#  fwoff_log=open( os.path.join(context['temp_directory'],'tmp_fw_off_4855.log'), 'w')
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties",
#                    "prp_write_mode", "prp_wm_async",
#                    "dbname", dbname ],
#                    stdout=fwoff_log, stderr=subprocess.STDOUT)
#  
#  fwoff_log.seek(0,2)
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_db_stats",
#                    "dbname", dbname, "sts_hdr_pages"],
#                    stdout=fwoff_log, stderr=subprocess.STDOUT)
#  flush_and_close( fwoff_log )
#  
#  #####################################################################
#  # Preparing script for ISQL that will do 'heavy DML':
#  
#  sql_cmd='''
#      recreate sequence g;
#      recreate table test(id int, s varchar( 36 ) unique using index test_s_unq);
#      recreate table stop(id int);
#      commit; 
#      set list on;
#      set transaction read committed;
#      set term ^;
#      execute block returns( inserted_rows varchar(20) ) as
#      begin
#        while ( not exists(select * from stop) ) do
#        begin
#          insert into test(id, s) values( gen_id(g,1), rpad('', 36, uuid_to_char(gen_uuid())) );
#        end
#        inserted_rows = iif( gen_id(g,0) > 0, 'OK, LOT OF.', 'FAIL: ZERO!');
#        suspend;
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  
#  f_heavy_dml_cmd=open( os.path.join(context['temp_directory'],'tmp_isql_4855.sql'), 'w')
#  f_heavy_dml_cmd.write(sql_cmd)
#  flush_and_close( f_heavy_dml_cmd )
#  
#  #####################################################################
#  # Starting ISQL in separate process with doing 'heavy DML' (bulk-inserts)  until table 'stop' 
#  # remains empty (this table will get one row in separate ISQL session, see below p_stopper):
#  
#  f_heavy_dml_log=open( os.path.join(context['temp_directory'],'tmp_isql_4855.log'), 'w')
#  p_heavy_dml = Popen([ context['isql_path'] , dsn, "-i", f_heavy_dml_cmd.name ], stdout=f_heavy_dml_log, stderr=subprocess.STDOUT)
#  
#  # Here we have to wait for sure that ISQL could establish its connect and starts DML 
#  # before we will run online-validation:
#  
#  # 16.03.2016: increased time delay because under some circumstances ISQL could not establish connect
#  # and this lead validation to start verify table TEST (which was not expected).
#  # Detected many times on CS/SC.
#  
#  time.sleep(4)
#  
#  
#  #####################################################################
#  # Doing online-validation.
#  # Use subprocess.call() with waiting in main thread for it will finish. 
#  
#  val_log=open( os.path.join(context['temp_directory'],'tmp_onval_4855.log'), 'w')
#  
#  val_log.write('Iteration #1:\\n')
#  val_log.seek(0,2)
#  subprocess.call( [ context['fbsvcmgr_path'], "localhost:service_mgr",
#                     "action_validate","val_lock_timeout","1",
#                     "dbname",dbname
#                   ],
#                   stdout=val_log, stderr=subprocess.STDOUT
#                 )
#  
#  time.sleep(2)
#  
#  # Iteration #2:
#  
#  val_log.seek(0,2)
#  val_log.write('\\n\\nIteration #2:\\n')
#  val_log.seek(0,2)
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_validate","val_lock_timeout","1",
#                   "dbname",dbname],
#                   stdout=val_log, stderr=subprocess.STDOUT)
#  flush_and_close( val_log )
#  
#  #####################################################################
#  
#  # Stopping ISQL that is doing now 'heavy DML' (bulk-inserts):
#  
#  f_stopper_cmd=open( os.path.join(context['temp_directory'],'tmp_stop_4855.sql'), 'w')
#  f_stopper_cmd.write('insert into stop(id) values(1); commit;')
#  flush_and_close( f_stopper_cmd )
#  p_stopper = subprocess.call([ context['isql_path'], dsn, "-i", f_stopper_cmd.name])
#  
#  # Stop working ISQL. NB: in rare cases this can lead to:
#  # + Statement failed, SQLSTATE = HY008
#  # + operation was cancelled
#  # + After line ... in file .../tmp_isql_4855.sql
#  
#  p_heavy_dml.terminate()
#  flush_and_close( f_heavy_dml_log )
#  
#  with open( f_heavy_dml_log.name,'r') as f:
#      print(f.read())
#  
#  with open( val_log.name,'r') as f:
#      print(f.read())
#  
#  
#  #####################################################################
#  # Cleanup:
#  time.sleep(1)
#  cleanup( (fwoff_log, val_log, f_heavy_dml_cmd, f_heavy_dml_log, f_stopper_cmd) )
#  
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
INSERTED_ROWS                   OK, LOT OF.
Iteration #1:
21:16:28.31 Validation started
21:16:28.31 Relation 128 (TEST)
21:16:29.31 Acquire relation lock failed
21:16:29.31 Relation 128 (TEST) : 1 ERRORS found
21:16:30.04 Relation 129 (STOP)
21:16:30.04   process pointer page    0 of    1
21:16:30.04 Relation 129 (STOP) is ok
21:16:30.04 Validation finished
Iteration #2:
21:16:32.46 Validation started
21:16:32.46 Relation 128 (TEST)
21:16:33.46 Acquire relation lock failed
21:16:33.46 Relation 128 (TEST) : 1 ERRORS found
21:16:35.09 Relation 129 (STOP)
21:16:35.09   process pointer page    0 of    1
21:16:35.09 Relation 129 (STOP) is ok
21:16:35.09 Validation finished
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


