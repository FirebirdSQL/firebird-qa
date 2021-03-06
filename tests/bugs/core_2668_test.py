#coding:utf-8
#
# id:           bugs.core_2668
# title:        Write note into log when automatic sweep is started
# decription:   
#                   In order to make database be 'ready' for sweep auto-start we:
#                   1. Launch ISQL in async. process (using Python subprocess.Popen() unit) which does:
#                     1.1. Change DB sweep interval to small value (100 selected).
#                     1.2. Create table and add one row in it (marked as 'LOCKED_FOR_PAUSE') + COMMIT.
#                     1.3. Start EXECUTE BLOCK with adding 150 of rows in autonomous transactions 
#                          (this lead eventually to difference Next - OIT =~ 150).
#                     1.4. Run execute block with ES/EDS which will establish new attachment (we specify
#                          there connection ROLE as some non-existent string, see ":v_role" usage below).
#                          This EB will try to UPDATE record which is LOCKED now by 1st ("main") attachment.
#                     ISQL will infinitelly hang since this moment.
#                   
#                   2. Run (in main Python thread) FBSVCMGR with:
#                     2.1. Moving database to SHUTDOWN state;
#                     2.2. Returning database back to ONLINE.
#                     2.3. Obtaining content of firebird.log and storing it in separate file ('f_fblog_before').
#                     2.4. Creating connect to DB and start transaction in order SWEEP will auto start.
#                     2.5. Take small delay (~2..3 seconds) in order to allow OS to finish writing new messages
#                          about SWEEP auto-start in firebird.log.
#                     2.6. Obtaining content of firebird.log and storing it in separate file ('f_fblog_after').
#                 
#                   3. Compare two files: f_fblog_before and f_fblog_after (using Python package "diff").
#                   Checked on:
#                       4.0.0.2173 SS/SC/CS
#                       3.0.7.33357 SS/SC/CS
#                       2.5.9.27152 SS/SC/CS
#                
# tracker_id:   CORE-2668
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import time
#  import subprocess
#  from subprocess import Popen
#  import difflib
#  import shutil
#  import re
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
#    return
#  
#  engine = str(db_conn.engine_version)
#  db_file=db_conn.database_name
#  
#  db_conn.close()
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  f_init_log = open( os.path.join(context['temp_directory'],'tmp_init_2668.log'), 'w')
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_sweep_interval", "100",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_init_log,
#                   stderr = subprocess.STDOUT
#                 )
#  
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_write_mode", "prp_wm_async",
#                    "dbname", db_file ],
#                    stdout = f_init_log,
#                    stderr = subprocess.STDOUT
#                 )
#  
#  f_work_sql=open( os.path.join(context['temp_directory'],'tmp_work_2668.sql'), 'w')
#  
#  sql_dml='''
#      recreate table test(s varchar(36) unique);
#      insert into test(s) values('LOCKED_FOR_PAUSE');
#      commit;
#  
#      set transaction read committed WAIT;
#  
#      update test set s = s where s = 'LOCKED_FOR_PAUSE';
#  
#      set term ^;
#      execute block as
#          declare n int = 150;
#          declare v_role varchar(31);
#      begin
#          while (n > 0) do 
#              in autonomous transaction do 
#              insert into test(s) values( rpad('', 36, uuid_to_char(gen_uuid()) ) ) 
#              returning :n-1 into n;
#  
#          v_role = left(replace( uuid_to_char(gen_uuid()), '-', ''), 31);
#      
#          begin
#              execute statement ('update test set s = s where s = ?') ('LOCKED_FOR_PAUSE')
#              on external 
#                  'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
#                  as user 'SYSDBA' password 'masterkey' role v_role
#              with autonomous transaction;
#          when any do
#              begin
#              end
#          end
#          
#      end
#      ^
#      set term ;^
#      set heading off;
#      select '-- shutdown me now --' from rdb$database;
#  '''
#  f_work_sql.write(sql_dml)
#  flush_and_close( f_work_sql )
#  
#  f_work_log=open( os.path.join(context['temp_directory'],'tmp_work_2668.log'), 'w')
#  
#  p_work_sql=Popen( [context['isql_path'], dsn, "-i", f_work_sql.name], stdout = f_work_log, stderr = subprocess.STDOUT )
#  time.sleep(3)
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_shutdown_mode", "prp_sm_full", "prp_shutdown_db", "0",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_init_log,
#                   stderr = subprocess.STDOUT
#                 )
#  
#  
#  p_work_sql.terminate()
#  flush_and_close( f_work_log )
#  
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_db_online",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_init_log,
#                   stderr = subprocess.STDOUT
#                 )
#  
#  flush_and_close( f_init_log )
#  
#  # 4 debug only -- shutil.copy2(db_file, os.path.splitext(db_file)[0]+'.copy.fdb')
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_2668_fblog_before.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  ###########################################
#  # Make connection to database.
#  # SWEEP should be auto started at this point:
#  ###########################################
#  
#  con_for_sweep_start=fdb.connect(dsn = dsn)
#  
#  # NOTE: it is mandatory to start transaction for auto-sweep:
#  con_for_sweep_start.begin()
#  
#  # _!_!_!_!_!_!_!_!_!_! do NOT reduce this delay: firebird.log get new messages NOT instantly !_!_!_!_!_!_!_!_
#  # Currently firebird.log can stay with OLD content if heavy concurrent workload exists on the same host!
#  time.sleep(2)
#  
#  con_for_sweep_start.close()
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_2668_fblog_after.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_after )
#  flush_and_close( f_fblog_after )
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_2668_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  pattern = re.compile('Sweep\\s+.*SWEEPER', re.IGNORECASE)
#  
#  # NB: difflib.unified_diff() can show line(s) that present in both files, without marking that line(s) with "+". 
#  # Usually these are 1-2 lines that placed just BEFORE difference starts.
#  # So we have to check output before display diff content: lines that are really differ must start with "+".
#  
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and pattern.search(line):
#              print('Expected line FOUND.')
#  
#  ###############################
#  # Cleanup.
#  time.sleep(1)
#  cleanup( [x.name for x in (f_init_log,f_work_sql,f_work_log,f_fblog_before,f_fblog_after,f_diff_txt) ] )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Expected line FOUND.
  """

@pytest.mark.version('>=2.5.2')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


