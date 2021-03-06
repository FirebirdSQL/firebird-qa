#coding:utf-8
#
# id:           bugs.core_4236
# title:        Database shutdown is reported as successfully completed before all active connections are in fact interrupted
# decription:   
#                   Test restores database with single table of following DDL:
#                       create table test(s varchar(1000));
#                       create index test_s on test(s);
#                   Than we start asynchronously several ISQL attachments which will do 'heavy DML' job: insert lot of rows in this table.
#                   After some delay (IMO, it should be at least 15..20 seconds) we start process of SHUTDOWN but with target mode = 'single'
#                   instead of 'full'. 
#                   After control will return from shutdown command, we can ensure that database has no any access and its file is closed 
#                   - this is done by call FBSVCMGR utility with arguments: action_repair rpr_validate_db rpr_full. This will launch process
#                   of database validation and it requires exclusive access, like 'gfix -v -full'.
#                   If validation will be able to open database in exclusive mode and do its job than NO any output will be produced. 
#                   Any problem with exclusive DB access will lead to error with text like: "database <db_file> shutdown".
#                   Finally, we check that:
#                   1) output of validation is really EMPTY - no any rows should present between two intentionally added lines 
#                      ("Validation start" and "validation finish" - they will be added only to improve visual perception of log);
#                   2) Every launched ISQL was really able to perform its task: at least to insert 100 row in the table, this result should
#                      be reflected in its log by message 'INS_PROGRESS ...' - it is suspended from EB every 100 rows.
#                   3) Every launched ISQL was really received exception with SQLCODE = HY000 - it also should be added at the end of ISQL log.
#               
#                   Checked on WI-V3.0.0.32253, SS/SC/CS (OS=Win XP), with 30 attachments that worked for 30 seconds.
#                   NB: Issue about hang CS was found during this test implementation, fixed here: 
#                   http://sourceforge.net/p/firebird/code/62737
#               
#                   Refactored 13-aug-2020:
#                       validation result is verified by inspecting difflib.unified_diff() result between firebird.log that was
#                       before and after validation: it must contain phrase "Validation finished: 0 errors"
#                       (we check that both validation *did* complete and absense of errors in DB).
#                   Checked on 4.0.0.2144 CS, 4.0.0.2151 SS.
#                
# tracker_id:   CORE-4236
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('VALIDATION FINISHED: 0 ERRORS.*', 'VALIDATION FINISHED: 0 ERRORS')]

init_script_1 = """"""

db_1 = db_factory(from_backup='core4236.fbk', init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import subprocess
#  from subprocess import Popen
#  import time
#  import re
#  import difflib
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_file=db_conn.database_name
#  db_conn.close()
#  
#  PLANNED_DML_ATTACHMENTS = 20
#  WAIT_FOR_ALL_CONNECTIONS_START_JOB = 20
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
#  def svc_get_fb_log( f_fb_log ):
#  
#    global subprocess
#    subprocess.call( [ context['fbsvcmgr_path'],
#                       "localhost:service_mgr",
#                       "action_get_fb_log"
#                     ],
#                     stdout=f_fb_log, stderr=subprocess.STDOUT
#                   )
#    return
#  
#  #--------------------------------------------
#  
#  dmltxt='''
#      set bail on;
#      set list on;
#      set term ^;
#      execute block returns(ins_progress int) as
#        declare n int = 100000;
#      begin
#        ins_progress=0;
#        while ( n > 0 ) do
#        begin
#          insert into test(s) values( rpad('', 500, uuid_to_char(gen_uuid())) );
#  
#          ins_progress = ins_progress + 1;
#          if ( mod(ins_progress, 100) = 0 ) then suspend;
#  
#          n = n - 1;
#        end
#      end
#      ^ set term ;^
#      quit;
#  '''
#  
#  f_sql_cmd=open( os.path.join(context['temp_directory'],'tmp_dml_4236.sql'), 'w')
#  f_sql_cmd.write(dmltxt)
#  flush_and_close(f_sql_cmd)
#  
#  isql_logs_list = []
#  isql_pids_list = []
#  
#  ########################################################################################
#  #  S T A R T I N G    S E V E R A L   I S Q L s    W I T H    H E A V Y    D M L   J O B
#  ########################################################################################
#  
#  for i in range(0, PLANNED_DML_ATTACHMENTS):
#      sqllog=open( os.path.join(context['temp_directory'],'tmp_dml_4236_'+str(i)+'.log'), 'w')
#      isql_logs_list.append(sqllog)
#  
#  for i in range(len(isql_logs_list)):
#      p_isql=Popen( [ context['isql_path'] , "localhost:"+db_file, "-i", f_sql_cmd.name ],
#                    stdout=isql_logs_list[i], stderr=subprocess.STDOUT
#                  )
#      isql_pids_list.append(p_isql)
#  
#  # Delay: let ISQL sessions do their job:
#  ########
#  time.sleep( WAIT_FOR_ALL_CONNECTIONS_START_JOB )
#  
#  # Move database to shutdown with ability to run after it validation (prp_sm_single):
#  
#  ###########################################################################################
#  # S H U T D O W N    D A T A B A S E   W I T H   T A R G E T   A C C E S S  = 'S I N G L E'
#  ###########################################################################################
#  f_shutdown_log=open( os.path.join(context['temp_directory'],'tmp_shutdown_4236.log'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "action_properties", "dbname", db_file,
#                   "prp_shutdown_mode", "prp_sm_single",
#                   "prp_force_shutdown", "0"],
#                  stdout=f_shutdown_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_shutdown_log )
#  
#  # At this point no further I/O should be inside database, including internal engine actions
#  # that relate to backouts. This mean that we *must* have ability to run DB validation in
#  # _exclusive_ mode, like gfix -v -full does.
#  
#  # Only for DEBUG: when this line is uncommented, validation should FAIL with message: database <db_file> shutdown. 
#  # Normally this line should be commented.
#  # conx = kdb.connect(dsn='localhost:'+db_file, user='SYSDBA', password='masterkey')
#  
#  # ........................ get firebird.log _before_ validation ..............................
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_4236_fblog_before.txt'), 'w')
#  svc_get_fb_log( f_fblog_before )
#  flush_and_close( f_fblog_before )
#  
#  
#  # Run validation that requires exclusive database access. 
#  # This process normally should produce NO output at all, it is "silent".
#  # If database currently is in use by engine or some attachments than it shoudl fail
#  # with message "database <db_file> shutdown."
#  
#  ######################################################################
#  #  V A L I D A T I O N    W I T H     E X C L U S I V E    A C C E S S
#  ######################################################################
#  f_validate_log=open( os.path.join(context['temp_directory'],'tmp_validate_4236.log'), 'w')
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "action_repair", "dbname", db_file,
#                   "rpr_validate_db", "rpr_full"],
#                  stdout=f_validate_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_validate_log )
#  
#  # ........................ get firebird.log _before_ validation ..............................
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_4236_fblog_after.txt'), 'w')
#  svc_get_fb_log( f_fblog_after )
#  flush_and_close( f_fblog_after )
#  
#  
#  # Compare firebird.log versions BEFORE and AFTER validation:
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_4236_diff.txt'), 'w')
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#  
#  # We are ionteresting only for line that contains result of validation:
#  p=re.compile('validation[	 ]+finished(:){0,1}[	 ]+\\d+[	 ]errors', re.IGNORECASE)
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and p.search(line):
#              print( 'DIFF IN FIREBIRD.LOG: ' + (' '.join(line.split()).upper()) )
#  
#  #///////////////////////////////////////////////////////////////////////////////////
#  
#  for i in range(len(isql_pids_list)):
#      isql_pids_list[i].terminate()
#  
#  for i in range(len(isql_logs_list)):
#      flush_and_close( isql_logs_list[i] )
#  
#  actual_dml_attachments = 0
#  logged_shutdown_count = 0
#  
#  for i in range(len(isql_logs_list)):
#      f = open(isql_logs_list[i].name, 'r')
#      sqllog=f.read()
#      f.close()
#  
#      if 'INS_PROGRESS' in sqllog:
#          actual_dml_attachments += 1
#      if 'SQLSTATE = HY000' in sqllog:
#          logged_shutdown_count += 1
#  
#  print("Check-1: how many DML attachments really could do their job ?")
#  if PLANNED_DML_ATTACHMENTS == actual_dml_attachments:
#       print("Result: OK, launched = actual")
#  else:
#       print("Result: BAD, launched<>actual")
#  
#  print("Check-2: how many sessions got SQLSTATE = HY000 on shutdown ?")
#  if PLANNED_DML_ATTACHMENTS == logged_shutdown_count:
#       print("Result: OK, launched = actual")
#  else:
#       print("Result: BAD, launched<>actual")
#  
#  # CLEANUP:
#  ##########
#  f_list = [x.name for x in [ f_sql_cmd,f_shutdown_log,f_validate_log,f_fblog_before,f_fblog_after,f_diff_txt ] + isql_logs_list ] #### + [ isql_logs_list ] ]
#  cleanup( f_list  )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DIFF IN FIREBIRD.LOG: + VALIDATION FINISHED: 0 ERRORS, 0 WARNINGS, 0 FIXED
    Check-1: how many DML attachments really could do their job ?
    Result: OK, launched = actual
    Check-2: how many sessions got SQLSTATE = HY000 on shutdown ?
    Result: OK, launched = actual
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


