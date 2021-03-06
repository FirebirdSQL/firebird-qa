#coding:utf-8
#
# id:           bugs.core_5275
# title:        CORE-5275: Expression index may become inconsistent if CREATE INDEX was interrupted after b-tree creation but before commiting
# decription:   
#                   This test (and CORE- ticket) has been created after wrong initial implementation of test for CORE-1746.
#                   Scenario:
#                   1. ISQL_1 is launched as child async. process, inserts 1000 rows and then falls in pause (delay) ~10 seconds;
#                   2. ISQL_2 is launched as child async. process in Tx = WAIT, tries to create index on the table which is handled
#                     by ISQL_1 and immediatelly falls in pause because of waiting for table lock.
#                   3. ISQL_3 is launched in SYNC mode and does 'DELETE FROM MON$ATTACHMENTS' thus forcing other attachments to be
#                     closed with raising 00803/connection shutdown.
#                   4. Repeat step 1. On WI-T4.0.0.258 this step lead to:
#                     "invalid SEND request (167), file: JrdStatement.cpp line: 325", 100% reproducilbe.
#               
#                   Checked on WI-V2.5.6.27017 (SC), WI-V3.0.1.32539 (SS/SC/CS), WI-T4.0.0.262 (SS) - works fine.
#               
#                   Beside above mentioned steps, we also:
#                   1) compare content of old/new firebird.log (difference): it should NOT contain line "consistency check";
#                   2) run database online validation: it should NOT report any error in the database.
#               
#                   :::::::::::::::::::::::::::::::::::::::: NB ::::::::::::::::::::::::::::::::::::
#                   18.08.2020. FB 4.x has incompatible behaviour with all previous versions since build 4.0.0.2131 (06-aug-2020):
#                   statement 'alter sequence <seq_name> restart with 0' changes rdb$generators.rdb$initial_value to -1 thus next call
#                   gen_id(<seq_name>,1) will return 0 (ZERO!) rather than 1. 
#                   See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d
#                   ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#                   This is considered as *expected* and is noted in doc/README.incompatibilities.3to4.txt
#               
#                   Because of this, it was decided to replace 'alter sequence restart...' with subtraction of two gen values:
#                   c = gen_id(<g>, -gen_id(<g>, 0)) -- see procedure sp_restart_sequences.
#               
#                   Checked on:
#                        4.0.0.2164 SS: 15.932s.
#                        4.0.0.2119 SS: 16.141s.
#                        4.0.0.2164 CS: 17.549s.
#                        3.0.7.33356 SS: 17.446s.
#                        3.0.7.33356 CS: 18.321s.
#                        2.5.9.27150 SC: 13.768s.
#                
# tracker_id:   CORE-5275
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = [('0: CREATE INDEX LOG: RDB_EXPR_BLOB.*', '0: CREATE INDEX LOG: RDB_EXPR_BLOB'), ('BULK_INSERT_START.*', 'BULK_INSERT_START'), ('.*KILLED BY DATABASE ADMINISTRATOR.*', ''), ('BULK_INSERT_FINISH.*', 'BULK_INSERT_FINISH'), ('CREATE_INDX_START.*', 'CREATE_INDX_START'), ('AFTER LINE.*', 'AFTER LINE'), ('RECORDS AFFECTED:.*', 'RECORDS AFFECTED:'), ('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]', ''), ('RELATION [0-9]{3,4}', 'RELATION')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import difflib
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file=db_conn.database_name
#  engine =str(db_conn.engine_version)
#  
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
#  def svc_get_fb_log( engine, f_fb_log ):
#  
#      import subprocess
#  
#      if engine.startswith('2.5'):
#          get_firebird_log_key='action_get_ib_log'
#      else:
#          get_firebird_log_key='action_get_fb_log'
#  
#      # C:\\MIX
#  irebird\\oldfb251in
#  bsvcmgr localhost:service_mgr -user sysdba -password masterkey action_get_ib_log
#      subprocess.call([ context['fbsvcmgr_path'],
#                        "localhost:service_mgr",
#                        get_firebird_log_key
#                      ],
#                       stdout=f_fb_log, stderr=subprocess.STDOUT
#                     )
#  
#      return
#  
#  sql_ddl='''
#      create or alter procedure sp_ins(n int) as begin end;
#      
#      recreate table test(x int unique using index test_x, s varchar(10) default 'qwerty' );
#  
#      set term  ^;
#      execute block as
#      begin
#          execute statement 'drop sequence g';
#          when any do begin end
#      end
#      ^
#      set term ;^
#      commit;
#      create sequence g;
#      commit;
#  
#      set term ^;
#      create or alter procedure sp_ins(n int) as
#      begin
#          while (n>0) do
#          begin
#              insert into test( x ) values( gen_id(g,1) );
#              n = n - 1;
#          end
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  runProgram('isql',[dsn],sql_ddl)
#  
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_5275_fblog_before.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  #########################################################
#  
#  rows_to_add=1000
#  
#  sql_bulk_insert='''    set bail on;
#      set list on;
#  
#      -- DISABLED 19.08.2020: alter sequence g restart with 0;
#  
#      delete from test;
#      commit;
#      set transaction lock timeout 10; -- THIS LOCK TIMEOUT SERVES ONLY FOR DELAY, see below auton Tx start.
#  
#      select current_timestamp as bulk_insert_start from rdb$database;
#      set term ^;
#      execute block as
#          declare i int;
#      begin
#          i = gen_id(g, -gen_id(g, 0)); -- restart sequence, since 19.08.2020
#          execute procedure sp_ins( %(rows_to_add)s );
#          begin
#              -- #########################################################
#              -- #######################  D E L A Y  #####################
#              -- #########################################################
#              in autonomous transaction do
#              insert into test( x ) values( %(rows_to_add)s ); -- this will cause delay because of duplicate in index
#          when any do 
#              begin
#                  i  =  gen_id(g,1);
#              end
#          end
#      end
#      ^
#      set term ;^
#      commit;
#      select current_timestamp as bulk_insert_finish from rdb$database;
#  '''
#  
#  sql_create_indx='''    set bail on;
#      set list on;
#      set blob all;
#      select 
#          iif( gen_id(g,0) > 0 and gen_id(g,0) < 1 + %(rows_to_add)s, 
#               'OK, IS RUNNING', 
#               iif( gen_id(g,0) <=0, 
#                    'WRONG: not yet started, current gen_id='||gen_id(g,0), 
#                    'WRONG: already finished, rows_to_add='||%(rows_to_add)s ||', current gen_id='||gen_id(g,0)
#                  )
#             ) as inserts_state, 
#          current_timestamp as create_indx_start 
#      from rdb$database;
#      set autoddl off;
#      commit;
#      
#      set echo on;
#      set transaction %(tx_decl)s;
#  
#      create index test_%(idx_name)s on test computed by( %(idx_expr)s ); 
#      set echo off;
#      commit;
#  
#      select 
#          iif(  gen_id(g,0) >= 1 + %(rows_to_add)s, 
#                'OK, FINISHED', 
#                'SOMETHING WRONG: current gen_id=' || gen_id(g,0)||', rows_to_add='||%(rows_to_add)s
#             ) as inserts_state
#      from rdb$database;
#      
#      set count on;
#      select
#          rdb$index_name
#          ,coalesce(rdb$unique_flag,0) as rdb$unique_flag
#          ,coalesce(rdb$index_inactive,0) as rdb$index_inactive
#          ,rdb$expression_source as rdb_expr_blob
#      from rdb$indices ri
#      where ri.rdb$index_name = upper( 'test_%(idx_name)s' )
#      ;
#      set count off;
#      set echo on;
#      set plan on;
#      select 1 from test where %(idx_expr)s > '' rows 0;
#      set plan off;
#      set echo off;
#      commit;
#      drop index test_%(idx_name)s;
#      commit;
#  '''
#  
#  sql_kill_att='''    set count on; 
#      set list on; 
#      commit; 
#      delete from mon$attachments where mon$attachment_id<>current_connection;
#  '''
#  
#  f_kill_att_sql = open( os.path.join(context['temp_directory'],'tmp_5275_kill_att.sql' ), 'w')
#  f_kill_att_sql.write( sql_kill_att )
#  flush_and_close( f_kill_att_sql )
#  
#  tx_param=['WAIT','WAIT']
#  
#  for i in range(len(tx_param)):
#  
#      f_bulk_insert_sql = open( os.path.join(context['temp_directory'],'tmp_5275_ins.sql'), 'w')
#      f_bulk_insert_sql.write(sql_bulk_insert % locals() )
#      flush_and_close( f_bulk_insert_sql )
#  
#      tx_decl=tx_param[i]
#      idx_name=tx_decl.replace(' ','_')
#      idx_expr="'"+idx_name+"'|| s"
#   
#      f_create_indx_sql = open( os.path.join(context['temp_directory'],'tmp_5275_idx_%s.sql' % str(i) ), 'w')
#      f_create_indx_sql.write( sql_create_indx % locals() )
#      flush_and_close( f_create_indx_sql )
#  
#      f_bulk_insert_log = open( os.path.join(context['temp_directory'],'tmp_5275_ins_%s.log' % str(i) ), 'w')
#      f_create_indx_log = open( os.path.join(context['temp_directory'],'tmp_5275_idx_%s.log' % str(i) ), 'w')
#  
#      p_bulk_insert=subprocess.Popen( [context['isql_path'], dsn, "-q", "-i", f_bulk_insert_sql.name ],
#                                     stdout = f_bulk_insert_log,
#                                     stderr = subprocess.STDOUT
#                                   )
#  
#      # 3.0 Classic: seems that it requires at least 2 seconds for ISQL be loaded into memory.
#      time.sleep(2)
#      
#      p_create_indx=subprocess.Popen( [context['isql_path'], dsn, "-q", "-i", f_create_indx_sql.name ],
#                                     stdout = f_create_indx_log,
#                                     stderr = subprocess.STDOUT
#                                   )
#      time.sleep(2)
#      
#      f_kill_att_log = open( os.path.join(context['temp_directory'],'tmp_5275_kill_att.log' ), 'w')
#  
#      subprocess.call( [context['isql_path'], dsn, "-q", "-i", f_kill_att_sql.name ],
#                                     stdout = f_kill_att_log,
#                                     stderr = subprocess.STDOUT
#                                   )
#      flush_and_close( f_kill_att_log )
#  
#      # 11.05.2017, FB 4.0 only!
#      # Following messages can appear after 'connection shutdown'
#      # (letter from dimitr, 08-may-2017 20:41):
#      #   isc_att_shut_killed: Killed by database administrator
#      #   isc_att_shut_idle: Idle timeout expired
#      #   isc_att_shut_db_down: Database is shutdown
#      #   isc_att_shut_engine: Engine is shutdown
#  
#      # do NOT remove this delay, otherwise ISQL logs in 2.5.x will contain NO text with error message
#      # STATEMENT FAILED, SQLSTATE = 08003 / CONNECTION SHUTDOWN:
#      time.sleep(1)
#  
#      p_create_indx.terminate()
#      p_bulk_insert.terminate()
#  
#      flush_and_close( f_bulk_insert_log )
#      flush_and_close( f_create_indx_log )
#  
#      with open( f_bulk_insert_log.name,'r') as f:
#          for line in f:
#              if line.split():
#                  print( str(i)+': BULK INSERTS LOG: '+line.strip().upper() )
#  
#      with open( f_create_indx_log.name,'r') as f:
#          for line in f:
#              if line.split():
#                  print( str(i)+': CREATE INDEX LOG: '+line.strip().upper() )
#     
#      with open( f_kill_att_log.name,'r') as f:
#          for line in f:
#              if line.split():
#                  print( str(i)+': KILL ATTACH LOG: '+line.upper() )
#  
#      # cleanup (nitermediate):
#      #########
#      time.sleep(1)
#      cleanup( (f_bulk_insert_sql, f_create_indx_sql, f_bulk_insert_log, f_create_indx_log, f_kill_att_log) )
#      
#  # ------------------------------------------------------------------------------------------    
#  
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_5275_fblog_after.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  # Now we can compare two versions of firebird.log and check their difference.
#  #################################
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_5275_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  # This should be empty:
#  #######################
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          # internal Firebird consistency check (invalid SEND request (167), file: JrdStatement.cpp line: 325)
#          if 'consistency check' in line:
#              print('NEW IN FIREBIRD.LOG: '+line.upper())
#  
#  
#  #--------------------------------------------------------------------------------------------
#  
#  f_validate_log=open( os.path.join(context['temp_directory'],'tmp_5275_validate.log'), "w")
#  f_validate_err=open( os.path.join(context['temp_directory'],'tmp_5275_validate.err'), "w")
#  
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "action_validate",
#                   "dbname", "$(DATABASE_LOCATION)bugs.core_5275.fdb"
#                  ],
#                  stdout=f_validate_log,
#                  stderr=f_validate_err)
#  flush_and_close( f_validate_log )
#  flush_and_close( f_validate_err )
#  
#  with open( f_validate_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( 'VALIDATION STDOUT: '+line.upper() )
#  
#  with open( f_validate_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( 'VALIDATION STDERR: '+line.upper() )
#  
#  # cleanup
#  #########
#  time.sleep(1)
#  cleanup( (f_validate_log, f_validate_err, f_kill_att_sql, f_fblog_before, f_fblog_after, f_diff_txt) )
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    0: BULK INSERTS LOG: BULK_INSERT_START
    0: BULK INSERTS LOG: STATEMENT FAILED, SQLSTATE = 08003
    0: BULK INSERTS LOG: CONNECTION SHUTDOWN
    0: BULK INSERTS LOG: AFTER LINE
    0: CREATE INDEX LOG: INSERTS_STATE                   OK, IS RUNNING
    0: CREATE INDEX LOG: CREATE_INDX_START
    0: CREATE INDEX LOG: SET TRANSACTION WAIT;
    0: CREATE INDEX LOG: CREATE INDEX TEST_WAIT ON TEST COMPUTED BY( 'WAIT'|| S );
    0: CREATE INDEX LOG: SET ECHO OFF;
    0: CREATE INDEX LOG: STATEMENT FAILED, SQLSTATE = 08003
    0: CREATE INDEX LOG: CONNECTION SHUTDOWN
    0: CREATE INDEX LOG: AFTER LINE
    0: KILL ATTACH LOG: RECORDS AFFECTED:
    1: BULK INSERTS LOG: BULK_INSERT_START
    1: BULK INSERTS LOG: STATEMENT FAILED, SQLSTATE = 08003
    1: BULK INSERTS LOG: CONNECTION SHUTDOWN
    1: BULK INSERTS LOG: AFTER LINE
    1: CREATE INDEX LOG: INSERTS_STATE                   OK, IS RUNNING
    1: CREATE INDEX LOG: CREATE_INDX_START
    1: CREATE INDEX LOG: SET TRANSACTION WAIT;
    1: CREATE INDEX LOG: CREATE INDEX TEST_WAIT ON TEST COMPUTED BY( 'WAIT'|| S );
    1: CREATE INDEX LOG: SET ECHO OFF;
    1: CREATE INDEX LOG: STATEMENT FAILED, SQLSTATE = 08003
    1: CREATE INDEX LOG: CONNECTION SHUTDOWN
    1: CREATE INDEX LOG: AFTER LINE
    1: KILL ATTACH LOG: RECORDS AFFECTED:
    VALIDATION STDOUT: 20:05:26.86 VALIDATION STARTED
    VALIDATION STDOUT: 20:05:26.86 RELATION 128 (TEST)
    VALIDATION STDOUT: 20:05:26.86   PROCESS POINTER PAGE    0 OF    1
    VALIDATION STDOUT: 20:05:26.86 INDEX 1 (TEST_X)
    VALIDATION STDOUT: 20:05:26.86 RELATION 128 (TEST) IS OK
    VALIDATION STDOUT: 20:05:26.86 VALIDATION FINISHED
  """

@pytest.mark.version('>=2.5.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


