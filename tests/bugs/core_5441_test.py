#coding:utf-8
#
# id:           bugs.core_5441
# title:        Cache physical numbers of often used data pages to reduce number of fetches of pointer pages
# decription:   
#                   We create table with single field, add several rows and create index.
#                   Number of these rows must be enough to fit all of them in the single data page.
#                   Than we do loop and query on every iteration one row, using PLAN INDEX.
#                   Only _first_ iteration should lead to reading PP (and this requires 1 fetch), 
#                   but all subseq. must require to read only DP. This should refect in trace as:
#                     * 4 fetches for 1st statement;
#                     * 3 fetches for statements starting with 2nd.
#                   Distinct number of fetches are accumulated in Python dict, and is displayed finally.
#                   We should have TWO distinct elements in this dict, and numbers in their values must
#                   differ at (N-1), where N = number of rows in the table.
#               
#                   Checked on:
#                   *  WI-T4.0.0.454 (22-nov-2016) -- number of fethes on every iteration is the same and equal to 4;
#                   *  WI-T4.0.0.460 (02-dec-2016) -- only at FIRST iter. fetches=4; for all subsequent loops fetches = 3.
#                   This proves that lot of PP scans are avoided and necessary data are taken from cache.
#               
#                   Also checked on:
#                   WI-V3.0.2.32677 (SS), WI-V3.0.2.32643 (SC/CS), WI-T4.0.0.519 (SS) -- all fine.
#               
#                
# tracker_id:   CORE-5441
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(x int primary key);
    commit;
    insert into test(x) select r from (
        select row_number()over() r 
        from rdb$types a,rdb$types b
        rows 10
    ) 
    order by rand();
    commit;

    set term ^; 
    create procedure sp_test as
        declare n int; 
        declare c int; 
    begin 
        n = 10;
        while( n > 0 ) do 
        begin
            execute statement ( 'select 1 from test where x = ? rows 1' ) ( :n ) into c;
            n = n - 1; 
        end 
    end^ 
    set term ;^
    commit;
  """

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
#  txt = '''# Generated auto, do not edit!
#    database=%[\\\\\\\\/]security?.fdb
#    {
#        enabled = false
#    }
#    database=%[\\\\\\\\/]bugs.core_5441.fdb
#    {
#        enabled = true
#        time_threshold = 0
#        include_filter = "%(select % from test where x = ?)%"
#        log_statement_finish = true
#  
#    }
#  '''
#  
#  f_trc_cfg=open( os.path.join(context['temp_directory'],'tmp_trace_5441.cfg'), 'w')
#  f_trc_cfg.write(txt)
#  flush_and_close( f_trc_cfg )
#  
#  # ##############################################################
#  # S T A R T   T R A C E   i n   S E P A R A T E    P R O C E S S
#  # ##############################################################
#  
#  f_trc_log=open( os.path.join(context['temp_directory'],'tmp_trace_5441.log'), "w")
#  f_trc_err=open( os.path.join(context['temp_directory'],'tmp_trace_5441.err'), "w")
#  
#  p_trace = Popen( [ context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_start' , 'trc_cfg', f_trc_cfg.name],stdout=f_trc_log,stderr=f_trc_err)
#  
#  time.sleep(1)
#  
#  # ####################################################
#  # G E T  A C T I V E   T R A C E   S E S S I O N   I D
#  # ####################################################
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  
#  f_trc_lst = open( os.path.join(context['temp_directory'],'tmp_trace_5441.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_list'], stdout=f_trc_lst)
#  flush_and_close( f_trc_lst )
#  
#  # !!! DO NOT REMOVE THIS LINE !!!
#  # time.sleep(1)
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
#  con1 = fdb.connect(dsn=dsn)
#  cur1=con1.cursor()
#  
#  #############################
#  # R U N    T E S T    P R O C
#  #############################
#  cur1.callproc('sp_test')
#  con1.close()
#  
#  # Let trace log to be entirely written on disk:
#  time.sleep(1)
#  
#  # ####################################################
#  # S E N D   R E Q U E S T    T R A C E   T O   S T O P
#  # ####################################################
#  if trcssn>0:
#      fn_nul = open(os.devnull, 'w')
#      subprocess.call([context['fbsvcmgr_path'], 'localhost:service_mgr', 'action_trace_stop','trc_id', trcssn], stdout=fn_nul)
#      fn_nul.close()
#  
#      # 23.02.2021. DELAY FOR AT LEAST 1 SECOND REQUIRED HERE!
#      # Otherwise trace log can remain empty.
#      time.sleep(2)
#  
#  p_trace.terminate()
#  flush_and_close( f_trc_log )
#  flush_and_close( f_trc_err )
#  
#  # Following file should be EMPTY:
#  ################
#  
#  f_list=(f_trc_err,)
#  for i in range(len(f_list)):
#     f_name=f_list[i].name
#     if os.path.getsize(f_name) > 0:
#         with open( f_name,'r') as f:
#             for line in f:
#                 print("Unexpected STDERR, file "+f_name+": "+line)
#  
#  fetches_distinct_amounts={}
#  
#  with open( f_trc_log.name,'r') as f:
#    for line in f:
#      if 'fetch(es)' in line:
#         words = line.split()
#         for k in range(len(words)):
#           if words[k].startswith('fetch'):
#             if not words[k-1] in fetches_distinct_amounts:
#               fetches_distinct_amounts[ words[k-1] ] = 1
#             else:
#               fetches_distinct_amounts[ words[k-1] ] += 1
#  
#  for k, v in sorted( fetches_distinct_amounts.items() ):
#    print( ''.join( ('fetches=',k) ), 'occured', v, 'times'  )
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( (f_trc_cfg, f_trc_lst, f_trc_log, f_trc_err) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    fetches=3 occured 9 times
    fetches=4 occured 1 times
  """

@pytest.mark.version('>=3.0.2')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


