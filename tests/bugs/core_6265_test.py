#coding:utf-8
#
# id:           bugs.core_6265
# title:        mapping rules destroyed by backup / restore
# decription:
#                   Confirmed bug on:  4.0.0.1796 CS; 3.0.6.33247 CS.
#                   Works fine on: 4.0.0.1806 SS; 3.0.6.33272 CS.
#
# tracker_id:   CORE-6265
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from io import BytesIO
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, role_factory, Role, temp_file

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import sys
#  import time
#  import subprocess
#  from subprocess import PIPE
#  from fdb import services
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
#
#  sql_init='''
#      create role boss;
#      create mapping map_boss using plugin win_sspi from user Bill to role boss;
#      commit;
#      create view v_map as
#      select
#          rdb$map_name,
#          rdb$map_using,
#          rdb$map_plugin,
#          rdb$map_db,
#          rdb$map_from_type,
#          rdb$map_from,
#          rdb$map_to_type,
#          rdb$map_to
#      from rdb$auth_mapping;
#      commit;
#      set list on;
#      set count on;
#      select * from v_map;
#  '''
#
#  f_init_sql = open( os.path.join(context['temp_directory'],'tmp_6265.sql'), 'w', buffering = 0)
#  f_init_sql.write( sql_init )
#  flush_and_close( f_init_sql )
#
#  f_init_log = open( '.'.join( (os.path.splitext( f_init_sql.name )[0], 'log') ), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], dsn, '-q', '-i', f_init_sql.name ], stdout = f_init_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_init_log )
#
#  this_restored_1=os.path.join(context['temp_directory'],'tmp_6265_1.tmp')
#  this_restored_2=os.path.join(context['temp_directory'],'tmp_6265_2.tmp')
#
#  cleanup( (this_restored_1, this_restored_2) )
#
#  # https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
#  #   output=`dmesg | grep hda`
#  #   becomes:
#  #   p1 = Popen(["dmesg"], stdout=PIPE)
#  #   p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
#  #   p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
#  #   output = p2.communicate()[0]
#  # gbak -b localhost:$fdb_init stdout | gbak -rep stdin localhost:$fdb_rest
#
#  # BACKUP-RESTORE #1:
#  # ~~~~~~~~~~~~~~~~~~
#  p_sender = subprocess.Popen( [ context['gbak_path'], '-b', dsn, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ context['gbak_path'], '-c', 'stdin',  'localhost:' + this_restored_1 ], stdin = p_sender.stdout, stdout = PIPE )
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#
#  #---------------------------------------------------------
#
#  # BACKUP-RESTORE #2:
#  # ~~~~~~~~~~~~~~~~~~
#  p_sender = subprocess.Popen( [ context['gbak_path'], '-b', 'localhost:' + this_restored_1, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ context['gbak_path'], '-c', 'stdin',  'localhost:' + this_restored_2 ], stdin = p_sender.stdout, stdout = PIPE )
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#
#  #----------------------------------------------------------
#
#  runProgram(context['isql_path'],[ 'localhost:' + this_restored_2 ], 'set list on; set count on; select * from v_map;')
#
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (this_restored_1, this_restored_2, f_init_sql, f_init_log) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$MAP_NAME                    MAP_BOSS
    RDB$MAP_USING                   P
    RDB$MAP_PLUGIN                  WIN_SSPI
    RDB$MAP_DB                      <null>
    RDB$MAP_FROM_TYPE               USER
    RDB$MAP_FROM                    BILL
    RDB$MAP_TO_TYPE                 1
    RDB$MAP_TO                      BOSS
    Records affected: 1
"""

init_ddl = """
    --create role boss;
    create mapping map_boss using plugin win_sspi from user Bill to role boss;
    commit;
    create view v_map as
    select
        rdb$map_name,
        rdb$map_using,
        rdb$map_plugin,
        rdb$map_db,
        rdb$map_from_type,
        rdb$map_from,
        rdb$map_to_type,
        rdb$map_to
    from rdb$auth_mapping;
    commit;
    set list on;
    set count on;
    select * from v_map;
"""

boss_role = role_factory('db_1', name='boss')

restored_db_1 = temp_file('tmp_6265_1.fdb')
restored_db_2 = temp_file('tmp_6265_2.fdb')

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action, boss_role: Role, restored_db_1: Path, restored_db_2: Path):
    act_1.isql(switches=['-q'], input=init_ddl)
    #
    backup = BytesIO()
    with act_1.connect_server() as srv:
        # BACKUP-RESTORE #1:
        srv.database.local_backup(database=act_1.db.db_path, backup_stream=backup)
        backup.seek(0)
        srv.database.local_restore(database=restored_db_1, backup_stream=backup)
        # BACKUP-RESTORE #2:
        backup.seek(0)
        backup.truncate()
        srv.database.local_backup(database=restored_db_1, backup_stream=backup)
        backup.seek(0)
        srv.database.local_restore(database=restored_db_2, backup_stream=backup)
    # Check
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[act_1.get_dsn(restored_db_2)], connect_db=False,
               input='set list on; set count on; select * from v_map;')
    assert act_1.clean_stdout == act_1.clean_expected_stdout
