#coding:utf-8
#
# id:           bugs.core_2879
# title:        Sweep could raise error : page 0 is of wrong type (expected 6, found 1)
# decription:
#                   Test receives content of firebird.log _before_ and _after_ running query that is show in the ticket.
#                   Then we compare these two files.
#                   Difference between them should relate ONLY to sweep start and finish details, and NOT about page wrong type.
#
#                   Checked on: WI-V2.5.7.27024, WI-V3.0.1.32570, WI-T4.0.0.316 -- all works OK.
#                   Refactored 01.02.2020, checked on:
#                       4.0.0.1759 SS: 4.754s.
#                       3.0.6.33240 SS: 3.704s.
#                       2.5.9.27119 SS: 6.607s.
#
# tracker_id:   CORE-2879
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
import time
import subprocess
from pathlib import Path
from difflib import unified_diff
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 2.5.1
# resources: None

substitutions_1 = [('^((?!start|finish|expected|page|wrong).)*$', '')] # ('\t+', ' '),

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import subprocess
#  from subprocess import Popen
#  import difflib
#  import time
#  import datetime
#  from datetime import datetime
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  engine = str(db_conn.engine_version)
#  db_file = db_conn.database_name # "$(DATABASE_LOCATION)bugs.core_2879.fdb"
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
#                     stdout=f_fb_log,
#                     stderr=subprocess.STDOUT
#                   )
#
#    return
#
#  #-----------------------------------------------------
#
#  sql_ddl='''    set list on;
#      set term ^;
#      execute block returns (dts timestamp, sql varchar(80)) as
#          declare i int;
#          declare s varchar(256);
#      begin
#          i = 1;
#          while (i < 32767) do
#          begin
#              s = 'tmp' || :i;
#              dts = 'now';
#              sql = 'create global temporary table ' || :s || ' (id int);';
#              execute statement sql with autonomous transaction;
#              suspend;
#
#              dts = 'now';
#              sql = 'drop table ' || :s || ';';
#              execute statement sql with autonomous transaction;
#              suspend;
#
#              i = i + 1;
#          end
#      end ^
#      set term ;^
#  '''
#
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_make_lot_GTT_2879.sql'), 'w', buffering = 0)
#  f_isql_cmd.write(sql_ddl)
#  f_isql_cmd.close()
#
#  # Get content of firebird.log BEFORE test:
#  ##########################################
#
#  f_fblog_before=open( os.path.join(context['temp_directory'],'tmp_2879_fblog_before.txt'), 'w', buffering = 0)
#  svc_get_fb_log( engine, f_fblog_before )
#  flush_and_close( f_fblog_before )
#
#  # LAUNCH ISQL ASYNCHRONOUSLY
#  ############################
#
#  f_isql_log=open( os.path.join(context['temp_directory'],'tmp_make_lot_GTT_2879.log'), 'w', buffering = 0)
#  p_isql=subprocess.Popen( [context['isql_path'], dsn, "-i", f_isql_cmd.name],
#                           stdout=f_isql_log,
#                           stderr=subprocess.STDOUT
#                         )
#  #------------
#  time.sleep(2)
#  #------------
#
#  # LAUNCH SWEEP while ISQL is working:
#  # ############
#  fbsvc_log=open( os.path.join(context['temp_directory'],'tmp_svc_2879.log'), 'w', buffering = 0)
#  subprocess.call( [ context['fbsvcmgr_path'],"localhost:service_mgr", "action_repair", "dbname", db_file, "rpr_sweep_db"], stdout=fbsvc_log, stderr=subprocess.STDOUT )
#  flush_and_close( fbsvc_log )
#
#  p_isql.terminate()
#  f_isql_log.close()
#
#
#  # Get content of firebird.log AFTER test:
#  #########################################
#
#  f_fblog_after=open( os.path.join(context['temp_directory'],'tmp_2879_fblog_after.txt'), 'w', buffering = 0)
#  svc_get_fb_log( engine, f_fblog_after )
#  flush_and_close( f_fblog_after )
#
#  # 07.08.2016
#  # DIFFERENCE in the content of firebird.log should be EMPTY:
#  ####################
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
#  f_diff_txt=open( os.path.join(context['temp_directory'],'tmp_2879_diff.txt'), 'w', buffering = 0)
#  f_diff_txt.write(difftext)
#  flush_and_close( f_diff_txt )
#
#  # NB: difflib.unified_diff() can show line(s) that present in both files, without marking that line(s) with "+".
#  # Usually these are 1-2 lines that placed just BEFORE difference starts.
#  # So we have to check output before display diff content: lines that are really differ must start with "+".
#
#  with open( f_diff_txt.name,'r') as f:
#      for line in f:
#          if line.startswith('+') and line.split('+'):
#              print(line.replace('+',' '))
#
#  # 01.02.2020. We have to change DB state to full shutdown and bring it back online
#  # in order to prevent "Object in use" while fbtest will try to drop this DB
#  #####################################
#  runProgram('gfix',[dsn,'-shut','full','-force','0'])
#  runProgram('gfix',[dsn,'-online'])
#
#
#
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( [i.name for i in (f_isql_cmd, f_isql_log, fbsvc_log, f_fblog_before,f_fblog_after, f_diff_txt)] )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Sweep is started by SYSDBA
    Sweep is finished
"""

isql_script = temp_file('test-script.sql')

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action, isql_script: Path, capsys):
    isql_script.write_text('''    set list on;
     set term ^;
     execute block returns (dts timestamp, sql varchar(80)) as
         declare i int;
         declare s varchar(256);
     begin
         i = 1;
         while (i < 32767) do
         begin
             s = 'tmp' || :i;
             dts = 'now';
             sql = 'create global temporary table ' || :s || ' (id int);';
             execute statement sql with autonomous transaction;
             suspend;

             dts = 'now';
             sql = 'drop table ' || :s || ';';
             execute statement sql with autonomous transaction;
             suspend;

             i = i + 1;
         end
     end ^
     set term ;^
     ''')
    with act_1.connect_server() as srv:
        # Get content of firebird.log BEFORE test
        srv.info.get_log()
        log_before = srv.readlines()
        p_isql = subprocess.Popen([act_1.vars['isql'], act_1.db.dsn, '-i', str(isql_script)],
                                 stderr=subprocess.STDOUT)
        time.sleep(2)
        # LAUNCH SWEEP while ISQL is working
        srv.database.sweep(database=act_1.db.db_path)
        p_isql.terminate()
        # Get content of firebird.log AFTER test
        srv.info.get_log()
        log_after = srv.readlines()
        for line in unified_diff(log_before, log_after):
            if line.startswith('+') and line.split('+'):
                print(line.replace('+', ' '))
        act_1.expected_stdout = expected_stdout_1
        act_1.stdout = capsys.readouterr().out
        assert act_1.clean_stdout == act_1.clean_expected_stdout


