#coding:utf-8
#
# id:           bugs.core_5704
# title:        Avoid UPDATE of RDB$DATABASE by ALTER DATABASE statement when possible
# decription:
#                   Instead of doing 'nbackup -L' plus fill database with lot of new data and then 'nbackup -N' with waiting for
#                   delta will be integrated into main file, we can get the same result by invoking 'alter database add difference file'
#                   statement in the 1st attachment in RC NO_REC_VERS and WITHOUT COMMITTING it, and then attempt to establish new connect
#                   using ES/EDS. Second attachment should be made without any problem, despite that transaction in 1st connect not yet
#                   committed or rolled back.
#
#                   Confirmed lock of rdb$database record (which leads to inability to establish new connect) on WI-V3.0.3.32837.
#                   Works fine on (SS, CS):
#                       3.0.3.32876: OK, 5.266s.
#                       4.0.0.852: OK, 5.594s.
#
# tracker_id:   CORE-5704
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
import subprocess
import time
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file
from firebird.driver import ShutdownMode, ShutdownMethod

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import subprocess
#  from subprocess import Popen
#  import time
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file = db_conn.database_name
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
#  usr=user_name
#  pwd=user_password
#  new_diff_file=os.path.join(context['temp_directory'],'tmp_new_diff_5704.tmp')
#  new_main_file=os.path.join(context['temp_directory'],'tmp_new_main_5704.tmp')
#
#  eds_query='''
#      set count on;
#      set list on;
#      set autoddl off;
#
#      set term ^;
#      create or alter procedure sp_connect returns(check_eds_result int) as
#         declare usr varchar(31);
#         declare pwd varchar(31);
#         declare v_sttm varchar(255) = 'select 1 from rdb$database';
#      begin
#         usr ='%(usr)s';
#         pwd = '%(pwd)s';
#         execute statement v_sttm
#         on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
#         as user usr password pwd
#         into check_eds_result;
#         suspend;
#      end
#      ^
#      set term ^;
#
#      commit;
#      set transaction read committed no record_version lock timeout 1;
#
#      alter database add difference file '%(new_diff_file)s';
#      select * from sp_connect;
#
#      rollback;
#      select * from rdb$files;
#      rollback;
#
#      set transaction read committed no record_version lock timeout 1;
#
#      alter database add file '%(new_main_file)s';
#      select * from sp_connect;
#      --select * from rdb$files;
#      rollback;
#      select * from rdb$files;
#  '''
#
#  f_eds_to_local_host_sql = open( os.path.join(context['temp_directory'],'tmp_local_host_5704.sql'), 'w')
#  f_eds_to_local_host_sql.write( eds_query % locals() )
#  flush_and_close( f_eds_to_local_host_sql )
#
#  f_eds_to_local_host_log = open( os.path.join(context['temp_directory'],'tmp_local_host_5704.log'), 'w')
#  f_eds_to_local_host_err = open( os.path.join(context['temp_directory'],'tmp_local_host_5704.err'), 'w')
#
#  # WARNING: we launch ISQL here in async mode in order to have ability to kill its process if it will hang!
#  ############################################
#  p_isql_to_local_host=subprocess.Popen( [context['isql_path'], dsn, "-i", f_eds_to_local_host_sql.name ],
#                   stdout = f_eds_to_local_host_log,
#                   stderr = f_eds_to_local_host_err
#                 )
#
#  time.sleep(3)
#
#  p_isql_to_local_host.terminate()
#  flush_and_close( f_eds_to_local_host_log )
#  flush_and_close( f_eds_to_local_host_err )
#
#
#  # Make DB shutdown and bring online because some internal server process still can be active!
#  # If we skip this step than runtime error related to dropping test DB can occur!
#  #########################################
#
#  f_db_reset_log=open( os.path.join(context['temp_directory'],'tmp_reset_5704.log'), 'w')
#  f_db_reset_err=open( os.path.join(context['temp_directory'],'tmp_reset_5704.err'), 'w')
#
#  f_db_reset_log.write('Point before DB shutdown.'+os.linesep)
#  f_db_reset_log.seek(0,2)
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_shutdown_mode", "prp_sm_full", "prp_shutdown_db", "0",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_db_reset_log,
#                   stderr = f_db_reset_err
#                 )
#  f_db_reset_log.write(os.linesep+'Point after DB shutdown.'+os.linesep)
#
#  subprocess.call( [context['fbsvcmgr_path'], "localhost:service_mgr",
#                    "action_properties", "prp_db_online",
#                    "dbname", db_file,
#                   ],
#                   stdout = f_db_reset_log,
#                   stderr = f_db_reset_err
#                 )
#
#  f_db_reset_log.write(os.linesep+'Point after DB online.'+os.linesep)
#  flush_and_close( f_db_reset_log )
#  flush_and_close( f_db_reset_err )
#
#  with open( f_eds_to_local_host_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('STDOUT in ISQL: ', ' '.join(line.split()) )
#
#  with open( f_eds_to_local_host_err.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED STDERR in '+f_eds_to_local_host_err.name+': '+line)
#
#  with open( f_db_reset_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('STDOUT in DB reset: ', ' '.join(line.split()) )
#
#  with open( f_db_reset_err.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('UNEXPECTED STDERR in '+f_db_reset_log.name+': '+line)
#
#  ###############################
#  # Cleanup.
#  time.sleep(1)
#
#  f_list=(
#       f_eds_to_local_host_sql
#      ,f_eds_to_local_host_log
#      ,f_eds_to_local_host_err
#      ,f_db_reset_log
#      ,f_db_reset_err
#  )
#  cleanup( f_list )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    CHECK_EDS_RESULT                1
    Records affected: 1
    Records affected: 0
    CHECK_EDS_RESULT                1
    Records affected: 1
    Records affected: 0
"""

eds_script = temp_file('eds_script.sql')
eds_output = temp_file('eds_script.out')
new_diff_file = temp_file('_new_diff_5704.tmp')
new_main_file = temp_file('new_main_5704.tmp')

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action, eds_script: Path, eds_output: Path, new_diff_file: Path,
           new_main_file: Path):
    eds_script.write_text(f"""
    set count on;
    set list on;
    set autoddl off;

    set term ^;
    create or alter procedure sp_connect returns(check_eds_result int) as
       declare usr varchar(31);
       declare pwd varchar(31);
       declare v_sttm varchar(255) = 'select 1 from rdb$database';
    begin
       usr ='{act_1.db.user}';
       pwd = '{act_1.db.password}';
       execute statement v_sttm
       on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
       as user usr password pwd
       into check_eds_result;
       suspend;
    end
    ^
    set term ^;

    commit;
    set transaction read committed no record_version lock timeout 1;

    alter database add difference file '{new_diff_file}';
    select * from sp_connect;

    rollback;
    select * from rdb$files;
    rollback;

    set transaction read committed no record_version lock timeout 1;

    alter database add file '{new_main_file}';
    select * from sp_connect;
    --select * from rdb$files;
    rollback;
    select * from rdb$files;
    """)
    #
    with open(eds_output, mode='w') as eds_out:
        p_eds_sql = subprocess.Popen([act_1.vars['isql'], '-i', str(eds_script),
                                      '-user', act_1.db.user,
                                      '-password', act_1.db.password, act_1.db.dsn],
                                     stdout=eds_out, stderr=subprocess.STDOUT)
        try:
            time.sleep(4)
        finally:
            p_eds_sql.terminate()
    # Ensure that database is not busy
    with act_1.connect_server() as srv:
        srv.database.shutdown(database=act_1.db.db_path, mode=ShutdownMode.FULL,
                              method=ShutdownMethod.FORCED, timeout=0)
        srv.database.bring_online(database=act_1.db.db_path)
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = eds_output.read_text()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
