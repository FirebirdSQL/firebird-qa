#coding:utf-8
#
# id:           bugs.core_4337
# title:        gfix -sweep makes "reconnect" when it is removed from mon$attachments by delete command (issued in another window)
# decription:
#                  We create table with very long char field and fill it with uuid data.
#                  Then we create index for this field and finally - delete all rows.
#                  Such table will require valuable time to be swept, about 4 seconds.
#
#                  After this, we launch asynchronously ISQL which makes delay ~2 seconds inside itself.
#                  Also, we launch trace for logging.
#
#                  After this we run 'gfix -sweep' in another process (synchronously).
#                  When delay in ISQL expires, ISQL connection executes 'DELETE FROM MON$ATTACHMENT' command
#                  which should kill gfix connection. This command is issued with 'set count on' for additional
#                  check that isql really could find this record in momn$attachments table.
#
#                  Process of GFIX should raise error 'connection shutdown'.
#                  Trace log should contain line with text 'SWEEP_FAILED' and after this line we should NOT
#                  discover any lines with 'ATTACH_DATABASE' event - this is especially verified.
#
#                  Finally, we compare content of firebird.log: new lines in it should contain messages about
#                  interrupted sweep ('error during sweep' and 'connection shutdown').
#
#                  Checked on WI-V3.0.2.32620 (SS/SC/CS), 4.0.0.420 (SS/SC).
#                  Total time of test run is ~25 seconds (data filling occupies about 3 seconds).
#
#                  11.05.2017: checked on WI-T4.0.0.638 - added filtering to messages about shutdown state, see comments below.
#                  26.09.2017: adjusted expected_stdout section to current FB 3.0+ versions: firebird.log now does contain info
#                  about DB name which was swept (see CORE-5610, "Provide info about database (or alias) which was in use...")
#                  Checked on:
#                       30Cs, build 3.0.3.32805: OK, 34.937s.
#                       30SS, build 3.0.3.32805: OK, 21.063s.
#                       40CS, build 4.0.0.748: OK, 31.313s.
#                       40SS, build 4.0.0.748: OK, 22.578s.
#
#               [pcisar] 19.11.2021
#               Small difference in reimplementation of sweep killer script
#               On v4.0.0.2496 COMMIT after delete from mon#attachments fails with:
#               STATEMENT FAILED, SQLSTATE = HY008, OPERATION WAS CANCELLED
#               Without commit this test PASSES, i.e. sweep is terminated with all outputs as expected
#
# tracker_id:   CORE-4337
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
import re
import time
import subprocess
from difflib import unified_diff
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file
from firebird.driver import DbWriteMode

# version: 3.0
# resources: None

substitutions_1 = [('[ ]+', ' '), ('TRACE_LOG:.* SWEEP_START', 'TRACE_LOG: SWEEP_START'),
                   ('TRACE_LOG:.* SWEEP_FAILED', 'TRACE_LOG: SWEEP_FAILED'),
                   ('TRACE_LOG:.* ERROR AT JPROVIDER::ATTACHDATABASE',
                    'TRACE_LOG: ERROR AT JPROVIDER::ATTACHDATABASE'),
                   ('.*KILLED BY DATABASE ADMINISTRATOR.*', ''),
                   ('TRACE_LOG:.*GFIX.EXE.*', 'TRACE_LOG: GFIX.EXE'),
                   ('OIT [0-9]+', 'OIT'), ('OAT [0-9]+', 'OAT'), ('OST [0-9]+', 'OST'),
                   ('NEXT [0-9]+', 'NEXT'),
                   ('FIREBIRD.LOG:.* ERROR DURING SWEEP OF .*TEST.FDB.*',
                    'FIREBIRD.LOG: + ERROR DURING SWEEP OF TEST.FDB')]

init_script_1 = """"""

db_1 = db_factory(page_size=16384, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  import difflib
#  import re
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file=db_conn.database_name
#  engine=str(db_conn.engine_version)
#  db_conn.close()
#
#  #-----------------------------------
#
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      os.fsync(file_handle.fileno())
#
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
#    global subprocess
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
#  #--------------------------------------------
#
#  # Change FW to OFF in order to speed up initial data filling:
#  ##################
#
#  fn_nul = open(os.devnull, 'w')
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_write_mode", "prp_wm_async",
#                    "dbname", db_file ],
#                    stdout = fn_nul,
#                    stderr = subprocess.STDOUT
#                 )
#  fn_nul.close()
#
#  f_work_sql=open( os.path.join(context['temp_directory'],'tmp_work_4337.sql'), 'w')
#
#  sql_dml='''
#      set list on;
#      select current_time from rdb$database;
#      recreate table t(s01 varchar(4000));
#      commit;
#      set term ^;
#      execute block as
#          declare n int = 20000;
#          declare w int;
#      begin
#          select f.rdb$field_length
#          from rdb$relation_fields rf
#          join rdb$fields f on rf.rdb$field_source=f.rdb$field_name
#          where rf.rdb$relation_name=upper('t')
#  	into w;
#
#          while (n>0) do
#              insert into t(s01) values( rpad('', :w, uuid_to_char(gen_uuid())) ) returning :n-1 into n;
#      end^
#      set term ;^
#      commit;
#      select count(*) check_total_cnt, min(char_length(s01)) check_min_length from t;
#
#      create index t_s01 on t(s01);
#      commit;
#
#      delete from t;
#      commit;
#      -- overall time for data filling , create index and delete all rows: ~ 3 seconds.
#      -- This database requires about 4 seconds to be swept (checked on P-IV 3.0 GHz).
#      select current_time from rdb$database;
#      --show database;
#      quit;
#  '''
#
#  f_work_sql.write(sql_dml)
#  flush_and_close( f_work_sql )
#
#  f_work_log=open( os.path.join(context['temp_directory'],'tmp_work_4337.log'), 'w')
#  f_work_err=open( os.path.join(context['temp_directory'],'tmp_work_4337.err'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-i", f_work_sql.name],
#                    stdout = f_work_log,
#                    stderr = f_work_err
#                  )
#
#  flush_and_close( f_work_log )
#  flush_and_close( f_work_err )
#
#  # REDUCE number of cache buffers in DB header in order to sweep make its work as long as possible
#  ################################
#  '''
#
#  temply disabled, see CORE-5385:
#  "Attempt to change number of buffers in DB header leads to crash (either using gfix -b ... or fbsvcmgr prp_page_buffers ... ). Only 4.0 SuperServer is affected."
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  fn_nul = open(os.devnull, 'w')
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_page_buffers", "100",
#                    "dbname", db_file ],
#                    stdout = fn_nul,
#                    stderr = subprocess.STDOUT
#                 )
#  fn_nul.close()
#  '''
#
#
#  # Change FW to ON (in order to make sweep life harder :))
#  ##################
#
#  fn_nul = open(os.devnull, 'w')
#  subprocess.call([ context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_write_mode", "prp_wm_sync",
#                    "dbname", db_file ],
#                    stdout = fn_nul,
#                    stderr = subprocess.STDOUT
#                 )
#  fn_nul.close()
#
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_4337_fblog_before.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_before )
#  flush_and_close( f_fblog_before )
#
#
#  trc30_cfg = '''# Trace config, format for 3.0. Generated auto, do not edit!
#  database=%[\\\\\\\\/]bugs.core_4337.fdb
#  {
#    enabled = true
#    log_sweep = true
#    log_errors = true
#    log_connections = true
#  }
#  services {
#    enabled = false
#    log_services = true
#    log_service_query = true
#  }
#  '''
#
#  f_trccfg=open( os.path.join(context['temp_directory'],'tmp_trace_4337.cfg'), 'w')
#  f_trccfg.write(trc30_cfg)
#  flush_and_close( f_trccfg )
#
#  # Starting trace session in new child process (async.):
#  #######################################################
#
#  f_trclog=open( os.path.join(context['temp_directory'],'tmp_trace_4337.log'), 'w')
#  f_trcerr=open( os.path.join(context['temp_directory'],'tmp_trace_4337.err'), 'w')
#
#  p_trace=Popen([context['fbsvcmgr_path'], "localhost:service_mgr",
#                 "action_trace_start",
#                  "trc_cfg", f_trccfg.name],
#                  stdout=f_trclog,
#                  stderr=f_trcerr
#               )
#
#  # Wait! Trace session is initialized not instantly!
#  time.sleep(1)
#
#
#  # Launch (async.) ISQL which will make small delay and then kill GFIX attachment:
#  ######################
#
#  sql_mon='''
#      set list on;
#
#      recreate table tmp4wait(id int);
#      commit;
#      insert into tmp4wait(id) values(1);
#      commit;
#
#      set transaction lock timeout 2; ------------------  D E L A Y
#      update tmp4wait set id=id;
#      select 'Waiting for GFIX start SWEEP' as " " from rdb$database;
#      set term ^;
#      execute block as
#      begin
#         in autonomous transaction do
#         begin
#             update tmp4wait set id=id;
#             when any do
#             begin
#                -- NOP --
#             end
#         end
#      end
#      ^
#      set term ;^
#      commit;
#      --select MON$PAGE_BUFFERS from mon$database;
#      select 'Starting to delete GFIX process from mon$attachments' as " " from rdb$database;
#      set count on;
#      delete from mon$attachments
#      where mon$remote_process containing 'gfix'
#      ;
#      commit;
#      set count off;
#      select 'Finished deleting GFIX process from mon$attachments' as " " from rdb$database;
#  '''
#
#  f_wait_sql=open( os.path.join(context['temp_directory'],'tmp_wait_4337.sql'), 'w')
#  f_wait_sql.write(sql_mon)
#  flush_and_close( f_wait_sql )
#
#  f_wait_log=open( os.path.join(context['temp_directory'],'tmp_wait_4337.log'), 'w')
#  f_wait_err=open( os.path.join(context['temp_directory'],'tmp_wait_4337.err'), 'w')
#  p_isql = subprocess.Popen( [ context['isql_path'], dsn, "-i", f_wait_sql.name],
#                    stdout = f_wait_log,
#                    stderr = f_wait_err
#                  )
#
#
#  # Launch GFIX -SWEEP (sync.). It should be killed by ISQL which we have launched previously
#  # after delay in its script will expire:
#  ########################################
#
#  f_gfix_log=open( os.path.join(context['temp_directory'],'tmp_gfix_4337.log'), 'w')
#  f_gfix_log.write('Point before GFIX -SWEEP.'+os.linesep)
#  f_gfix_log.seek(0,2)
#  subprocess.call( [ context['gfix_path'], dsn, "-sweep"],
#                    stdout = f_gfix_log,
#                    stderr = subprocess.STDOUT
#                  )
#
#
#  f_gfix_log.seek(0,2)
#  f_gfix_log.write('Point after GFIX -SWEEP.')
#
#  # Small delay to be sure that ISQL was successfully completed.
#  ##############
#
#  time.sleep(2)
#
#  p_isql.terminate()
#
#  flush_and_close( f_wait_log )
#  flush_and_close( f_wait_err )
#  flush_and_close( f_gfix_log )
#
#
#  #####################################################
#  # Getting ID of launched trace session and STOP it:
#
#  # Save active trace session info into file for further parsing it and obtain session_id back (for stop):
#  f_trclst=open( os.path.join(context['temp_directory'],'tmp_trace_4337.lst'), 'w')
#
#  subprocess.call([context['fbsvcmgr_path'], "localhost:service_mgr",
#                   "action_trace_list"],
#                   stdout=f_trclst, stderr=subprocess.STDOUT
#                 )
#  f_trclst.close()
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
#  p_trace.terminate()
#  flush_and_close( f_trclog )
#  flush_and_close( f_trcerr )
#
#  # Make DB shutdown and bring online because some internal server process still can be active!
#  # If we skip this step than runtime error related to dropping test DB can occur!
#  #########################################
#
#  f_db_reset_log=open( os.path.join(context['temp_directory'],'tmp_reset_4337.log'), 'w')
#
#  f_db_reset_log.write('Point before DB shutdown.'+os.linesep)
#  f_db_reset_log.seek(0,2)
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_shutdown_mode", "prp_sm_full", "prp_shutdown_db", "0",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_db_reset_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_db_reset_log.write(os.linesep+'Point after DB shutdown.'+os.linesep)
#
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_db_online",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_db_reset_log,
#                   stderr = subprocess.STDOUT
#                 )
#
#  f_db_reset_log.write(os.linesep+'Point after DB online.'+os.linesep)
#  flush_and_close( f_db_reset_log )
#
#
#  # Get content of firebird.log AFTER test finish.
#  #############################
#
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_4337_fblog_after.txt'), 'w')
#  svc_get_fb_log( engine, f_fblog_after )
#  flush_and_close( f_fblog_after )
#
#  # _!_!_!_!_!_!_!_!_!_! do NOT reduce this delay: firebird.log get new messages NOT instantly !_!_!_!_!_!_!_!_
#  # Currently firebird.log can stay with OLD content if heavy concurrent workload exists on the same host!
#  # ??? DISABLED 18.02.2021, BUT STILL IN DOUBT...  time.sleep(5)
#
#  # Compare firebird.log versions BEFORE and AFTER this test:
#  ######################
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_4337_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#
#  # Check logs:
#  #############
#
#  # 1. Log of GFIX -SWEEP should contain:
#  '''
#     Point before GFIX -SWEEP.
#     connection shutdown
#     Point after GFIX -SWEEP.
#  '''
#
#  # 11.05.2017, FB 4.0 only!
#  # Following messages can appear after 'connection shutdown'
#  # (letter from dimitr, 08-may-2017 20:41):
#  #   isc_att_shut_killed: Killed by database administrator
#  #   isc_att_shut_idle: Idle timeout expired
#  #   isc_att_shut_db_down: Database is shutdown
#  #   isc_att_shut_engine: Engine is shutdown
#
#  with open( f_gfix_log.name,'r') as f:
#      for line in f:
#          if line.strip():
#              print( line.upper() )
#
#
#  # 2. Log of ISQL that was launched to kill 'GFIX -SWEEP' attachment should contain:
#  '''
#  MSG                             Waiting for GFIX start SWEEP
#  MSG                             Starting to delete GFIX process from mon$attachments
#  Records affected: 1
#  MSG                             Finished deleting GFIX process from mon$attachments
#  '''
#  with open( f_wait_log.name,'r') as f:
#      for line in f:
#          if line.strip():
#              print( 'ISQL LOG: ' + line.upper() )
#
#
#  # 3. Log of TRACE should contain 'SWEEP_FAILED' only 'DETACH_DATABASE' event after this line:
#  '''
#      2016-10-26T21:49:06.4040 (2184:00D33200) SWEEP_FAILED
#      	C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\BUGS.CORE_4337.FDB (ATT_16, SYSDBA:NONE, NONE, TCPv4:127.0.0.1/1406)
#      	C:\\MIX\\Firebird
#  b40\\gfix.exe:4700
#         2061 ms, 17273 read(s), 781 write(s), 538838 fetch(es), 146541 mark(s)
#
#      2016-10-26T21:49:06.4040 (2184:00D33200) ERROR AT JProvider::attachDatabase
#      	C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\BUGS.CORE_4337.FDB (ATT_16, SYSDBA:NONE, NONE, TCPv4:127.0.0.1/1406)
#      	C:\\MIX\\Firebird
#  b40\\gfix.exe:4700
#      335544856 : connection shutdown
#
#      2016-10-26T21:49:06.4040 (2184:00D33200) DETACH_DATABASE
#      	C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\BUGS.CORE_4337.FDB (ATT_16, SYSDBA:NONE, NONE, TCPv4:127.0.0.1/1406)
#      	C:\\MIX\\Firebird
#  b40\\gfix.exe:4700
#  '''
#
#  found_sweep_failed=0
#  with open( f_trclog.name,'r') as f:
#      for line in f:
#          if 'SWEEP_FAILED' in line:
#              print( 'TRACE_LOG:' + (' '.join(line.split()).upper()) )
#              found_sweep_failed = 1
#
#          if found_sweep_failed == 1 and ('ATTACH_DATABASE' in line):
#              print( 'TRACE: ATTACH DETECTED AFTER SWEEP FAILED! ' )
#              print( 'TRACE_LOG:' + (' '.join(line.split()).upper()) )
#
#
#  # Output should contain only ONE message with 'SWEEP_FAILED', and NO any rows related to ATTACH_DATABASE.
#
#  # 4. Difference between old and current firebird.log should be like this:
#  '''
#      +
#      +CSPROG	Wed Oct 26 21:49:04 2016
#      +	Sweep is started by SYSDBA
#      +	Database "C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\BUGS.CORE_4337.FDB"
#      +	OIT 21, OAT 22, OST 19, Next 25
#      +
#      +
#      +CSPROG	Wed Oct 26 21:49:06 2016
#      +	Error during sweep:
#      +	connection shutdown
#  '''
#
#  # 5. Log of fbsvcmgr when it did shutdown DB and bring it back online should be EMPTY.
#  # NB: difflib.unified_diff() can show line(s) that present in both files, without marking that line(s) with "+".
#  # Usually these are 1-2 lines that placed just BEFORE difference starts.
#  # So we have to check output before display diff content: lines that are really differ must start with "+".
#
#  pattern  = re.compile("\\+[\\s]+OIT[ ]+[0-9]+,[\\s]*OAT[\\s]+[0-9]+,[\\s]*OST[\\s]+[0-9]+,[\\s]*NEXT[\\s]+[0-9]+")
#  # OIT 160, OAT 159, OST 159, Next 161
#
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+'):
#              if  'sweep'.upper() in line.upper() or 'connection'.upper() in line.upper() or pattern.match(line.upper()):
#                  print( 'FIREBIRD.LOG: ' + (' '.join(line.split()).upper()) )
#
#  # 6. ERROR logs of ISQL for initial data filling should be EMPTY:
#  with open( f_work_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED ERROR IN ISQL WHEN DID INITIAL DATA FILLING: ' + line)
#
#  # 7. ERROR logs of ISQL for initial data filling should be EMPTY:
#  with open( f_wait_err.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED ERROR IN ISQL WHEN MADE DELAY AND WAITING: ' + line)
#
#
#  # Cleanup.
#  ###############################
#  time.sleep(1)
#  cleanup( [i.name for i in (f_work_sql,f_work_log,f_work_err,f_fblog_before,f_trccfg,f_trclog,f_trcerr,f_wait_sql,f_wait_log,f_wait_err,f_gfix_log,f_trclst,f_db_reset_log,f_fblog_after,f_diff_txt) ] )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

make_garbage_1 = """
    set list on;
    select current_time from rdb$database;
    recreate table t(s01 varchar(4000));
    commit;
    set term ^;
    execute block as
        declare n int = 20000;
        declare w int;
    begin
        select f.rdb$field_length
        from rdb$relation_fields rf
        join rdb$fields f on rf.rdb$field_source=f.rdb$field_name
        where rf.rdb$relation_name=upper('t')
        into w;

        while (n>0) do
            insert into t(s01) values( rpad('', :w, uuid_to_char(gen_uuid())) ) returning :n-1 into n;
    end^
    set term ;^
    commit;
    select count(*) check_total_cnt, min(char_length(s01)) check_min_length from t;

    create index t_s01 on t(s01);
    commit;

    delete from t;
    commit;
    -- overall time for data filling , create index and delete all rows: ~ 3 seconds.
    -- This database requires about 4 seconds to be swept (checked on P-IV 3.0 GHz).
    select current_time from rdb$database;
    --show database;
    quit;
"""

expected_stdout_1 = """
    CONNECTION SHUTDOWN
    ISQL LOG: WAITING FOR GFIX START SWEEP
    ISQL LOG: STARTING TO DELETE GFIX PROCESS FROM MON$ATTACHMENTS
    ISQL LOG: RECORDS AFFECTED: 1
    ISQL LOG: FINISHED DELETING GFIX PROCESS FROM MON$ATTACHMENTS
    TRACE_LOG: SWEEP_FAILED
    FIREBIRD.LOG: + SWEEP IS STARTED BY SYSDBA
    FIREBIRD.LOG: + OIT, OAT, OST, NEXT
    FIREBIRD.LOG: + ERROR DURING SWEEP OF TEST.FDB
    FIREBIRD.LOG: + CONNECTION SHUTDOWN
"""

sweep_killer_script_1 = temp_file('killer.sql')
sweep_killer_out_1 = temp_file('killer.out')
sweep_killer_err_1 = temp_file('killer.err')
sweep_out_1 = temp_file('sweep.out')

trace_1 = ['time_threshold = 0',
           'log_errors = true',
           'log_sweep = true',
           'log_connections = true',
           ]

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys, sweep_killer_script_1: Path, sweep_killer_out_1: Path,
           sweep_killer_err_1: Path, sweep_out_1: Path):
    sweep_killer_script_1.write_text("""
    set list on;

    recreate table tmp4wait(id int);
    commit;
    insert into tmp4wait(id) values(1);
    commit;

    set transaction lock timeout 2; ------------------  D E L A Y
    update tmp4wait set id=id;
    select 'Waiting for GFIX start SWEEP' as " " from rdb$database;
    set term ^;
    execute block as
    begin
       in autonomous transaction do
       begin
           update tmp4wait set id=id;
           when any do
           begin
              -- NOP --
           end
       end
    end
    ^
    set term ;^
    commit;
    --select MON$PAGE_BUFFERS from mon$database;
    select 'Starting to delete GFIX process from mon$attachments' as " " from rdb$database;
    set count on;
    delete from mon$attachments where mon$remote_process containing 'gfix';
    -- On v4.0.0.2496 COMMIT fails with: STATEMENT FAILED, SQLSTATE = HY008, OPERATION WAS CANCELLED
    -- Without commit this test PASSES, i.e. sweep is terminated with all outputs as expected
    -- commit;
    set count off;
    select 'Finished deleting GFIX process from mon$attachments' as " " from rdb$database;
    """)
    with act_1.connect_server() as srv:
        # get firebird log before action
        srv.info.get_log()
        log_before = srv.readlines()
        # Change FW to OFF in order to speed up initial data filling
        srv.database.set_write_mode(database=act_1.db.db_path, mode=DbWriteMode.ASYNC)
        # make garbage
        act_1.isql(switches=[], input=make_garbage_1)
        # REDUCE number of cache buffers in DB header in order to sweep make its work as long as possible
        srv.database.set_default_cache_size(database=act_1.db.db_path, size=100)
        # Change FW to ON (in order to make sweep life harder :))
        srv.database.set_write_mode(database=act_1.db.db_path, mode=DbWriteMode.SYNC)
    # Start trace
    with act_1.trace(db_events=trace_1):
        # Launch (async.) ISQL which will make small delay and then kill GFIX attachment
        with open(sweep_killer_out_1, 'w') as killer_out, \
             open(sweep_killer_err_1, 'w') as killer_err:
            p_killer = subprocess.Popen([act_1.vars['isql'],
                                            '-i', str(sweep_killer_script_1),
                                           '-user', act_1.db.user,
                                           '-password', act_1.db.password, act_1.db.dsn],
                                           stdout=killer_out, stderr=killer_err)
            try:
                time.sleep(2)
                # Launch GFIX -SWEEP (sync.). It should be killed by ISQL which we have
                # launched previously after delay in its script will expire:
                act_1.expected_stderr = 'We expect errors'
                act_1.gfix(switches=['-sweep', act_1.db.dsn])
                gfix_out = act_1.stdout
                gfix_err = act_1.stderr
            finally:
                p_killer.terminate()
    #
    # get firebird log after action
    with act_1.connect_server() as srv:
        srv.info.get_log()
        log_after = srv.readlines()
    # construct final stdout for checks
    print(gfix_out.upper())
    print(gfix_err.upper())
    # sweep filler output
    for line in sweep_killer_out_1.read_text().splitlines():
        if line:
            print('ISQL LOG:', line.upper())
    for line in sweep_killer_err_1.read_text().splitlines():
        if line:
            print('ISQL ERR:', line.upper())
    # Trace log
    found_sweep_failed = 0
    for line in act_1.trace_log:
        if 'SWEEP_FAILED' in line:
            print('TRACE_LOG:' + (' '.join(line.split()).upper()))
            found_sweep_failed = 1
        if found_sweep_failed == 1 and ('ATTACH_DATABASE' in line):
            print('TRACE: ATTACH DETECTED AFTER SWEEP FAILED! ')
            print('TRACE_LOG:' + (' '.join(line.split()).upper()))
    #
    pattern  = re.compile("\\+[\\s]+OIT[ ]+[0-9]+,[\\s]*OAT[\\s]+[0-9]+,[\\s]*OST[\\s]+[0-9]+,[\\s]*NEXT[\\s]+[0-9]+")
    for line in unified_diff(log_before, log_after):
        if line.startswith('+'):
            line = line.upper()
            if 'SWEEP' in line or 'CONNECTION' in line or pattern.match(line):
                print( 'FIREBIRD.LOG: ' + (' '.join(line.split())) )
    #
    # check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
