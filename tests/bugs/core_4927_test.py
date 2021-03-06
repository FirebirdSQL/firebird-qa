#coding:utf-8
#
# id:           bugs.core_4927
# title:        IIF function prevents the condition from being pushed into the union for better optimization
# decription:   
#                  1. Obtain engine_version from built-in context variable.
#                  2. Make config for trace in proper format according to FB engine version,
#                     with adding invalid element 'foo' instead on boolean ('true' or 'false')
#                  3. Launch trace session in separate child process using 'FBSVCMGR action_trace_start'
#                  4. Run ISQL with calling test SP.
#                  5. Stop trace session. Output its log with filtering only messages related to ticket notes.
#               
#                  Trace log for FB 2.5 builds before rev. 62200 ( http://sourceforge.net/p/firebird/code/62200 )
#                  contained tables which does NOT contain data which we are looked for (marked as "<<<"):
#               
#                  Table                             Natural     Index
#                  ****************************************************
#                  HEADER_2100                             1
#                  DETAIL_1000                                       1 <<<
#                  DETAIL_1200                                       1
#                  DETAIL_2000                                       1 <<<
#                  DETAIL_2100                                       1
#                  DETAIL_3300                                       1 <<<
#               
#                  Here we check that trace log will contain only TWO tables: HEADER_2100 and DETAIL_2100.
#                  Bug affected only 2.5.x. Test checked on: WI-V2.5.5.26928, built at: 2015-09-08 00:13:06 UTC (rev 62201)
#                  
#                  ::: NB :::
#                  Several delays (time.sleep) added in main thread because of OS buffering. Couldn't switch this buffering off.
#                
# tracker_id:   CORE-4927
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = [('^((?!HEADER_|DETAIL_).)*$', ''), ('HEADER_2100.*', 'HEADER_2100'), ('DETAIL_2100.*', 'DETAIL_2100')]

init_script_1 = """
    create or alter procedure sp_test as begin end;
    recreate view vd_union as select 1 id from rdb$database;
    recreate table header_2100(dd_id int, ware_id int, snd_optype_id int);
    recreate table detail_1000 (ware_id int,snd_optype_id int,rcv_optype_id int,snd_id int);
    recreate table detail_1200 (ware_id int,snd_optype_id int,rcv_optype_id int,snd_id int);
    recreate table detail_2000 (ware_id int,snd_optype_id int,rcv_optype_id int,snd_id int);
    recreate table detail_2100 (ware_id int,snd_optype_id int,rcv_optype_id int,snd_id int);
    recreate table detail_3300 (ware_id int,snd_optype_id int,rcv_optype_id int,snd_id int);
    recreate view vd_union as
    select 'd1000' src,q.*
    from detail_1000 q
    union all
    select 'd1200', q.*
    from detail_1200 q
    union all
    select 'd2000', q.*
    from detail_2000 q
    union all
    select 'd2100', q.*
    from detail_2100 q
    union all
    select 'd3300', q.*
    from detail_3300 q
    ;
    commit;

    set term ^;
    create or alter procedure sp_test returns(result int) as 
    begin
        for
            select count(*)
            from (
                select
                    d.dd_id,
                    d.ware_id,
                    iif(1 = 0, 3300, 2100) as snd_optype_id -- this caused engine to unnecessary scans of tables which did not contain data searched for
                from header_2100 d
            ) d
            left join vd_union qd on
                qd.ware_id = d.ware_id
                and qd.snd_optype_id = d.snd_optype_id
                and qd.rcv_optype_id is not distinct from 3300
                and qd.snd_id = d.dd_id
            into result
        do 
           suspend;
    end
    ^
    set term ;^
    commit;
    
    insert into header_2100(dd_id, ware_id, snd_optype_id) values(1, 11, 2100);
    commit;
    
    insert into detail_1000 (ware_id,snd_optype_id,rcv_optype_id,snd_id) values( 11, 1000, 1200, 1);
    insert into detail_1200 (ware_id,snd_optype_id,rcv_optype_id,snd_id) values( 11, 1200, 2000, 1);
    insert into detail_2000 (ware_id,snd_optype_id,rcv_optype_id,snd_id) values( 11, 2000, 2100, 1);
    insert into detail_2100 (ware_id,snd_optype_id,rcv_optype_id,snd_id) values( 11, 2100, 3300, 1);
    insert into detail_3300 (ware_id,snd_optype_id,rcv_optype_id,snd_id) values( 11, 3300, null, 1);
    commit;
    
    create index d1000_wsrs on detail_1000 (ware_id,snd_optype_id,rcv_optype_id,snd_id);
    create index d1200_wsrs on detail_1200 (ware_id,snd_optype_id,rcv_optype_id,snd_id);
    create index d2000_wsrs on detail_2000 (ware_id,snd_optype_id,rcv_optype_id,snd_id);
    create index d2100_wsrs on detail_2100 (ware_id,snd_optype_id,rcv_optype_id,snd_id);
    create index d3300_wsrs on detail_3300 (ware_id,snd_optype_id,rcv_optype_id,snd_id);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#  from subprocess import Popen
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
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
#  
#  #####################################################
#  
#  txt25 = '''# Trace config, format for 2.5. Generated auto, do not edit!
#  <database %[\\\\\\\\/]bugs.core_4927.fdb>
#    enabled true
#    time_threshold 0 
#    log_statement_finish true
#    print_perf true
#  </database>
#  '''
#  
#  # NOTES ABOUT TRACE CONFIG FOR 3.0:
#  # 1) Header contains `database` clause in different format vs FB 2.5: its data must be enclosed with '{' '}'
#  # 2) Name and value must be separated by EQUALITY sign ('=') in FB-3 trace.conf, otherwise we get runtime error:
#  #    element "<. . .>" have no attribute value set
#  
#  txt30 = '''# Trace config, format for 3.0. Generated auto, do not edit!
#  database=%[\\\\\\\\/]bugs.core_4927.fdb
#  {
#    enabled = true
#    time_threshold = 0
#    log_statement_finish = true
#    print_perf = true
#  }
#  '''
#  
#  f_trccfg=open( os.path.join(context['temp_directory'],'tmp_trace_4927.cfg'), 'w')
#  if engine.startswith('2.5'):
#      f_trccfg.write(txt25)
#  else:
#      f_trccfg.write(txt30)
#  
#  flush_and_close( f_trccfg )
#  
#  #####################################################
#  # Starting trace session in new child process (async.):
#  
#  f_trclog=open( os.path.join(context['temp_directory'],'tmp_trace_4927.log'), 'w')
#  # Execute a child program in a new process, redirecting STDERR to the same target as of STDOUT:
#  p_trace=Popen([context['fbsvcmgr_path'], "localhost:service_mgr",
#                 "action_trace_start",
#                  "trc_cfg", f_trccfg.name],
#                  stdout=f_trclog, stderr=subprocess.STDOUT)
#  
#  # Wait! Trace session is initialized not instantly!
#  time.sleep(1)
#  
#  sqltxt='''
#      set list on;
#      select result from sp_test;
#  '''
#  
#  runProgram('isql',[dsn],sqltxt)
#  
#  # do NOT remove this otherwise trace log can contain only message about its start before being closed!
#  time.sleep(3)
#  
#  # Getting ID of launched trace session and STOP it:
#  ###################################################
#  
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  f_trclst=open( os.path.join(context['temp_directory'],'tmp_trace_4927.lst'), 'w')
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_list"],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  trcssn=0
#  with open( f_trclst.name,'r') as f:
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
#  f_trclst=open(f_trclst.name,'a')
#  f_trclst.seek(0,2)
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_stop",
#                   "trc_id",trcssn],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  flush_and_close( f_trclst )
#  
#  # Terminate child process of launched trace session (though it should already be killed):
#  p_trace.terminate()
#  flush_and_close( f_trclog )
#  
#  with open( f_trclog.name,'r') as f:
#      for line in f:
#          print(line)
#  
#  # do NOT remove this delay otherwise get access error 'Windows 32'
#  # (The process cannot access the file because it is being used by another process):
#  time.sleep(1)
#  
#  # CLEANUP
#  #########
#  cleanup( (f_trccfg, f_trclst, f_trclog) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    HEADER_2100
    DETAIL_2100
  """

@pytest.mark.version('>=2.5.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


