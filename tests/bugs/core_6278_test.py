#coding:utf-8
#
# id:           bugs.core_6278
# title:        Efficient table scans for DBKEY-based range conditions
# decription:   
#                   We create table with very wide column and add there about 300 rows from rdb$types, with random data
#                   (in order to prevent RLE-compression which eventually can reduce number of data pages).
#                   Then we extract all values of rdb$db_key from this table and take into processing two of them.
#                   First value has 'distance' from starting db_key = 1/3 of total numbers of rows, second has similar
#                   distance from final db_key.
#                   Finally we launch trace and start query with SCOPED expression for RDB$DB_KEY:
#                       select count(*) from tmp_test_6278 where rdb$db_key between ? and ?
#               
#                   Trace must contain after this explained plan with "lower bound, upper bound" phrase and table statistics
#                   which shows number of reads = count of rows plus 1.
#                   ::: NOTE:::
#                   Before fix trace table statistics did not reflect scoped WHERE-expression on RDB$DB_KEY column.
#               
#                   Checked on 4.0.0.1869 - works fine.
#                
# tracker_id:   CORE-6278
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
#  import re
#  from fdb import services
#  from subprocess import Popen
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
#  txt = '''
#      database=%[\\\\\\\\/]security?.fdb
#      {
#          enabled = false
#      }
#      database=%[\\\\\\\\/]bugs.core_6278.fdb
#      {
#          enabled = true
#          log_initfini = false
#          time_threshold = 0
#          log_errors = false
#          log_statement_finish = true
#  
#          exclude_filter = "%(execute block)%"
#          include_filter = "%(select count)%"
#  
#          #log_statement_prepare = true
#          print_perf = true
#          print_plan = true
#          explain_plan = true
#      }
#  '''
#  
#  f_trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trace_6278.cfg'), 'w', buffering = 0)
#  f_trc_cfg.write(txt)
#  flush_and_close( f_trc_cfg )
#  
#  # ##############################################################
#  # S T A R T   T R A C E   i n   S E P A R A T E    P R O C E S S
#  # ##############################################################
#  
#  f_trc_log=open( os.path.join(context['temp_directory'],'tmp_trace_6278.log'), "w", buffering = 0)
#  f_trc_err=open( os.path.join(context['temp_directory'],'tmp_trace_6278.err'), "w", buffering = 0)
#  
#  # ::: NB ::: DO NOT USE 'localhost:service_mgr' here! Use only local protocol:
#  p_trace = Popen( [ context['fbsvcmgr_path'], 'service_mgr', 'action_trace_start' , 'trc_cfg', f_trc_cfg.name],stdout=f_trc_log,stderr=f_trc_err)
#  
#  time.sleep(1)
#  
#  # ####################################################
#  # G E T  A C T I V E   T R A C E   S E S S I O N   I D
#  # ####################################################
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  
#  f_trc_lst = open( os.path.join(context['temp_directory'],'tmp_trace_6278.lst'), 'w', buffering = 0)
#  subprocess.call([ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_list'], stdout=f_trc_lst)
#  flush_and_close( f_trc_lst )
#  
#  # !!! DO NOT REMOVE THIS LINE !!!
#  time.sleep(1)
#  
#  trcssn=0
#  with open( f_trc_lst.name,'r') as f:
#      for line in f:
#          i=1
#          if 'Session ID' in line:
#              for word in line.split():
#                  if i==3:
#                      trcssn=word
#                  i=i+1
#              break
#  
#  # Result: `trcssn` is ID of active trace session. Now we have to terminate it:
#  
#  #------------------------------------------------
#  sql = '''
#      recreate table tmp_test_6278(s varchar(32700));
#      insert into tmp_test_6278 select lpad('',32700,gen_uuid()) from rdb$types;
#      commit;
#      set heading off;
#      set term ^;
#      execute block returns(
#         count_intermediate_rows int
#      ) as
#          declare dbkey_1 char(8) character set octets;
#          declare dbkey_2 char(8) character set octets;
#          declare sttm varchar(255);
#      begin
#         select max(iif( ri=1, dbkey, null)), max(iif( ri=2, dbkey, null))
#         from (
#             select dbkey, row_number()over(order by dbkey) ri
#             from (
#                 select
#                     dbkey
#                    ,row_number()over(order by dbkey) ra
#                    ,row_number()over(order by dbkey desc) rd
#                 from (select rdb$db_key as dbkey from tmp_test_6278)
#             )
#             where
#                 ra = (ra+rd)/3
#                 or rd = (ra+rd)/3
#         ) x 
#         into dbkey_1, dbkey_2;
#  
#         sttm = q'{select count(*) from tmp_test_6278 where rdb$db_key between ? and ?}';
#         execute statement (sttm) (dbkey_1, dbkey_2) into count_intermediate_rows;
#         suspend;
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  
#  f_sql_cmd=open( os.path.join(context['temp_directory'],'tmp_c6278_run.sql'), 'w')
#  f_sql_cmd.write(sql)
#  flush_and_close( f_sql_cmd )
#  
#  f_isql_log=open( os.path.join(context['temp_directory'],'tmp_c6278_run.log'), 'w', buffering = 0)
#  f_isql_err=open( os.path.join(context['temp_directory'],'tmp_c6278_run.err'), 'w', buffering = 0)
#  
#  ######################
#  # S T A R T    I S Q L
#  ######################
#  subprocess.call( [ context['isql_path'], dsn, '-q', '-i', f_sql_cmd.name],
#                   stdout=f_isql_log,
#                   stderr=f_isql_err
#                 )
#  flush_and_close( f_isql_log )
#  flush_and_close( f_isql_err )
#  
#  #------------------------------------------------
#  
#  # Let trace log to be entirely written on disk:
#  time.sleep(1)
#  
#  # ####################################################
#  # S E N D   R E Q U E S T    T R A C E   T O   S T O P
#  # ####################################################
#  if trcssn>0:
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call([ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_stop','trc_id', trcssn], stdout=fn_nul)
#      fn_nul.close()
#      # DO NOT REMOVE THIS LINE:
#      time.sleep(1)
#  
#  p_trace.terminate()
#  flush_and_close( f_trc_log )
#  flush_and_close( f_trc_err )
#  
#  
#  allowed_patterns = [ 
#      re.compile(' Table "TMP_TEST_6278"', re.IGNORECASE)
#     ,re.compile('TMP_TEST_6278\\s+\\d+', re.IGNORECASE)
#  ]
#  
#  #----------------------------------------------------------------------
#  
#  # Parse STDOUT result of ISQL: extract from log result of
#  # select count(*) from tmp_test_6278 where rdb$db_key between ? and ?.
#  # It must be ~1/3 of rows in RDB$TYPES table for empty database:
#  
#  with open(f_isql_log.name, 'r') as f:
#      for line in f:
#          if line.split():
#              count_intermediate_rows = int( line.rstrip().split()[0] )
#              break
#  
#  # Result of STDERR for ISQL must be empty:
#  with open(f_isql_err.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED STDERR IN ISQL RESULT: ' + line)
#  
#  #---------------------------------------------------------------------
#  
#  # Parse trace log:
#  # 1. Extract token from EXPLAINED plan: it must contain "lower bound, upper bound" clause that was introduced by this ticket;
#  # 2. Number of reads (currently they are shown under NATURAL read column)  must be equal to result obtained in ISQL, plus 1.
#  #    NB: before fix this number of reads was always equal to the total number of records, regardless on presense of additional
#  #    WHERE-condition on rdb$db_key column.
#  # -----------------------------------------
#  with open(f_trc_log.name, 'r') as f:
#      for line in f:
#          for p in allowed_patterns:
#              if p.search(line):
#                  if line.startswith('TMP_TEST_6278'):
#                      trace_reads_statistics = int( line.rstrip().split()[1] )
#                      print( 'Reads difference: ' + ('EXPECTED.' if (trace_reads_statistics - count_intermediate_rows) <= 1 else 'UNEXPECTED: ' + str( (trace_reads_statistics - count_intermediate_rows) ) ) )
#                  else:
#                      print(line)
#  
#  # CLEANUP:
#  ##########
#  time.sleep(1)
#  cleanup( ( f_trc_log, f_trc_err, f_trc_cfg, f_trc_lst, f_isql_log, f_isql_err, f_sql_cmd ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    -> Table "TMP_TEST_6278" Full Scan (lower bound, upper bound)
    Reads difference: EXPECTED.
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


