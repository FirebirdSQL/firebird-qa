#coding:utf-8
#
# id:           bugs.core_5435
# title:        Badly selective index could be used for extra filtering even if selective index is used for sorting
# decription:   
#                  Test creates table and fills it with data like it was specified in the source ticket,
#                  but query has been CHANGED after discuss with dimitr (see letter 19-jan-2017 08:43):
#                  instead of 'f01 is null' we use 'f01 = 1' because actually problem that was fixed 
#                  is NOT related with NULL handling.
#                  Usage of NULL will hide effect of improvement in optimizer because there is old bug
#                  in FB from early years which prevent engine from fast navigate on index (i.e. PLAN ORDER)
#                  when expression is like 'is NULL'.
#                  ----------------------------------
#                  
#                  Implementation details: we start trace and run ISQL with query, then stop trace, open its log
#                  and parse it with seeking lines with 'plan (' and 'fetch(es)'. 
#                  Expected plan: 
#                      PLAN (TEST ORDER TEST_F01_ID) -- confirmed on WI-T4.0.0.503 
#                      0 ms, 3 read(s), 44 fetch(es)
#                  WRONG (ineffective) plan:
#                      PLAN (TEST ORDER TEST_F01_ID INDEX (TEST_F02_ONLY)) -- detected on WI-T4.0.0.463
#                      21 ms, 115 read(s), 157 fetch(es)
#                  Value of fetches is compared with threshold (currently = 80) which was received after several runs.
#                
# tracker_id:   CORE-5435
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=8192, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
#  from fdb import services
#  from subprocess import Popen
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file = db_conn.database_name
#  # Obtain engine version:
#  engine = str(db_conn.engine_version)
#  
#  db_conn.close()
#  
#  FETCHES_THRESHOLD = 80
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
#  # Change FW to OFF in order to speed up initial data filling:
#  ##################
#  fn_nul = open(os.devnull, 'w')
#  
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_write_mode", "prp_wm_async",
#                    "dbname", db_file ],
#                    stdout = fn_nul,
#                    stderr = subprocess.STDOUT
#                 )
#  
#  fn_nul.close()
#  
#  #####################
#  # Prepare table: add data.
#  
#  sql_init='''
#    recreate table test
#    (
#        id int not null,
#        f01 int,
#        f02 int
#    );
#  
#    set term ^;
#    create or alter procedure sp_add_init_data(a_rows_to_add int)
#    as
#        declare n int;
#        declare i int = 0;
#    begin
#        n = a_rows_to_add;
#        while ( i < n ) do
#        begin
#            insert into test(id, f01, f02) values( :i, nullif(mod(:i, :n/20), 0), iif( mod(:i,3)<2, 0, 1) )
#            returning :i+1 into i;
#        end
#    end
#    ^
#    set term ^;
#    commit;
#  
#    execute procedure sp_add_init_data( 300000 );
#    commit;
#  
#    create index test_f01_id on test(f01, id);
#    create index test_f02_only on test(f02); 
#    commit;
#  '''
#  
#  sql_cmd=open(os.path.join(context['temp_directory'],'tmp_core_5435.sql'), 'w')
#  sql_cmd.write(sql_init)
#  flush_and_close( sql_cmd )
#  
#  sql_log=open(os.path.join(context['temp_directory'],'tmp_core_5435.log'),'w')
#  sql_err=open(os.path.join(context['temp_directory'],'tmp_core_5435.err'),'w')
#  
#  subprocess.call([ context['isql_path'], dsn, "-i", sql_cmd.name],stdout=sql_log, stderr=sql_err)
#  
#  flush_and_close( sql_log )
#  flush_and_close( sql_err )
#  
#  #########################
#  
#  txt = '''# Generated auto, do not edit!
#    database=%[\\\\\\\\/]security?.fdb
#    {
#        enabled = false
#    }
#    database=%[\\\\\\\\/]bugs.core_5435.fdb
#    {
#        enabled = true
#        time_threshold = 0
#        log_statement_finish = true
#        print_plan = true
#        print_perf = true
#    }
#  '''
#  
#  f_trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trace_5435.cfg'), 'w')
#  f_trc_cfg.write(txt)
#  flush_and_close( f_trc_cfg )
#  
#  # ##############################################################
#  # S T A R T   T R A C E   i n   S E P A R A T E    P R O C E S S
#  # ##############################################################
#  
#  f_trc_log=open( os.path.join(context['temp_directory'],'tmp_trace_5435.log'), "w")
#  f_trc_err=open( os.path.join(context['temp_directory'],'tmp_trace_5435.err'), "w")
#  
#  p_trace = Popen( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_start' , 'trc_cfg', f_trc_cfg.name],stdout=f_trc_log,stderr=f_trc_err)
#  
#  
#  sql_run='''
#    set list on;
#    select count(*) cnt_check 
#    from (
#        select *
#        from test               -- ############################################################################
#        where f01 = 1 and f02=0 -- <<< ::: NB ::: we check here 'f01 = 1' rather than 'f01 is NULL' <<< !!! <<<
#        order by f01, id        -- ############################################################################
#    )
#    ;
#  '''
#  
#  sql_cmd=open(os.path.join(context['temp_directory'],'tmp_core_5435.sql'), 'w')
#  
#  sql_cmd.write(sql_run)
#  flush_and_close( sql_cmd )
#  
#  sql_log=open(os.path.join(context['temp_directory'],'tmp_core_5435.log'),'w')
#  sql_err=open(os.path.join(context['temp_directory'],'tmp_core_5435.err'),'w')
#  
#  subprocess.call([ context['isql_path'], dsn, "-i", sql_cmd.name],stdout=sql_log, stderr=sql_err)
#  
#  flush_and_close( sql_log )
#  flush_and_close( sql_err )
#  
#  # 01-mar-2021: do NOT remove delay from here.
#  # It must be at least 2 seconds, otherwise trace log will not be fulfilled
#  # when run on Linux!
#  time.sleep(2)
#  
#  # ####################################################
#  # G E T  A C T I V E   T R A C E   S E S S I O N   I D
#  # ####################################################
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  
#  f_trc_lst = open( os.path.join(context['temp_directory'],'tmp_trace_5435.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_list'], stdout=f_trc_lst)
#  flush_and_close( f_trc_lst )
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
#  # ####################################################
#  # S E N D   R E Q U E S T    T R A C E   T O   S T O P
#  # ####################################################
#  if trcssn>0:
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_stop','trc_id', trcssn], stdout=fn_nul)
#      fn_nul.close()
#  else:
#      print('Trace session was finished forcedly: could not find its trc_id.')
#  
#  p_trace.terminate()
#  flush_and_close( f_trc_log )
#  flush_and_close( f_trc_err )
#  
#  run_with_plan=''
#  num_of_fetches=-1
#  
#  with open( f_trc_log.name,'r') as f:
#      for line in f:
#          if line.lower().startswith('plan ('):
#              run_with_plan = line.upper()
#          if 'fetch(es)' in line:
#              words = line.split()
#              for k in range(len(words)):
#                  if words[k].startswith('fetch'):
#                      num_of_fetches = int( words[k-1] )
#  
#  if run_with_plan and num_of_fetches>0:
#      print(run_with_plan)
#      print('Number of fetches: acceptable.' if num_of_fetches < FETCHES_THRESHOLD else 'Too much fetches %(num_of_fetches)s: more than threshold = %(FETCHES_THRESHOLD)s' % locals())
#  else:
#      print('Trace log was not fulfilled: can not find lines with PLAN and/or STATISTICS. Increase delays in the test code!')
#      print('Content of trace log:')
#      print('=' * 21)
#      f=open( f_trc_log.name,'r')
#      for r in f.readlines():
#          print(r)
#      f.close()
#      print('=' * 21)
#      
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( (f_trc_cfg, f_trc_lst, f_trc_log, f_trc_err, sql_log, sql_err, sql_cmd) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST ORDER TEST_F01_ID)
    Number of fetches: acceptable.
  """

@pytest.mark.version('>=3.0.2')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


