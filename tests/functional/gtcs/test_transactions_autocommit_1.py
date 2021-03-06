#coding:utf-8
#
# id:           functional.gtcs.transactions_autocommit_1
# title:        GTCS/tests/AUTO_COMMIT.1.ESQL. AUTO COMMIT must preserve changes that were made by all DML even if ROLLBACK is issued.
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/AUTO_COMMIT.1.ESQL.script
#               
#                   Test creates three tables (test_1, test_2 and test_3) and AI-trigger for one of them (test_1).
#                   This trigger does INSERTs into test_2 and test_3.
#               
#                   Then we add record into test_1 and after this INSERT its trigger add records into test_2 and test_3.
#                   After this we make transaction ROLLED BACK and check how many records are preserved.
#                   Expected result: each of three tables must have one record in itself, i.e. result looks like we did COMMIT rather than ROLLBACK.
#               
#                   NB: we use custom TPB with fdb.isc_tpb_autocommit in order to start DML transactions in AUTOCOMMIT=1 mode.
#                   Checked on:
#                       4.0.0.1812 SS: 2.344s.
#                       4.0.0.1767 SC: 2.339s.
#                       4.0.0.1810 SS: 2.151s.
#                       3.0.6.33273 SS: 1.023s.
#                       3.0.6.33240 SC: 1.301s.
#                       3.0.6.33247 CS: 2.598s.
#                       2.5.6.27020 SS: 3.156s.
#                       2.5.9.27149 SC: 0.323s.
#                       2.5.9.27143 CS: 1.159s.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import subprocess
#  import inspect
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#      for f in f_names_list:
#         if type(f) == file:
#            del_name = f.name
#         elif type(f) == str:
#            del_name = f
#         else:
#            print('Unrecognized type of element:', f, ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#      
#  #--------------------------------------------
#  
#  sql_init='''
#      set bail on;
#      recreate table test_1 (x integer);
#      recreate table test_2 (x integer);
#      recreate table test_3 (x integer);
#      commit;
#      set term ^;
#      create or alter trigger trg_test1_ai for test_1 active after insert position 0 as
#      begin
#          insert into test_2 values (new.x * 7);
#          insert into test_3 values (new.x * 777);
#      end ^
#      set term ;^
#      commit;
#  '''
#  
#  f_init_sql = open( os.path.join(context['temp_directory'],'tmp_gtcs_tx_ac2.sql'), 'w', buffering = 0)
#  f_init_sql.write( sql_init )
#  flush_and_close( f_init_sql )
#  
#  f_init_log = open( '.'.join( (os.path.splitext( f_init_sql.name )[0], 'log') ), 'w', buffering = 0)
#  f_init_err = open( '.'.join( (os.path.splitext( f_init_sql.name )[0], 'err') ), 'w', buffering = 0)
#  
#  subprocess.call( [ context['isql_path'], dsn, '-q', '-i', f_init_sql.name ], stdout = f_init_log, stderr = f_init_err)
#  
#  flush_and_close( f_init_log )
#  flush_and_close( f_init_err )
#  
#  CUSTOM_TX_PARAMS = ( [ fdb.isc_tpb_nowait, fdb.isc_tpb_autocommit ] )
#  
#  con1 = fdb.connect( dsn = dsn )
#  tra1 = con1.trans( default_tpb = CUSTOM_TX_PARAMS )
#  
#  tra1.begin()
#  cur1=tra1.cursor()
#  
#  cur1.execute('select mon$auto_commit from mon$transactions where mon$transaction_id = current_transaction')
#  for r in cur1:
#      print( 'mon$auto_commit:', r[0] )
#  
#  cur1.execute( 'insert into test_1 values(?)', ( 777,) )
#  
#  #----------------------   R O L L B A C K  -----------------------
#  
#  tra1.rollback()
#  cur1.close()
#  con1.close()
#  
#  #----------------------   R E C O N N E C T  -----------------------
#  
#  con2 = fdb.connect( dsn = dsn )
#  cur2=con2.cursor()
#  cur2.execute("select 'test_1' tab_name, x from test_1 union all select 'test_2', x from test_2 union all select 'test_3', x from test_3")
#  # Here we must see records from ALL THREE tables.
#  for r in cur2:
#      print( r[0], r[1] )
#  
#  cur2.close()
#  con2.close()
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( ( f_init_sql, f_init_log, f_init_err) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    mon$auto_commit: 1
    test_1 777
    test_2 5439
    test_3 603729
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


