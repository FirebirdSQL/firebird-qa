#coding:utf-8
#
# id:           bugs.core_6233
# title:        Wrong dependencies of stored function on view after backup and restore
# decription:
#                   We make backup of this test DB and restore it to other name using PIPE mechanism
#                   in order to skip creation of unneeded .fbk file
#                   See: https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
#                   Confirmed bug on 4.0.0.1740.
#                   Checked on 4.0.0.1743: works OK.
#                   Checked result of backporting fix to on 3.0.6.33265: OK.
#
# tracker_id:   CORE-6233
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from io import BytesIO
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """
    set bail on;
    create or alter procedure p1 as begin end;
    create or alter function f1 returns integer as begin end;
    commit;

    set term ^;
    create or alter view v1 as
      select 1 as n from rdb$database
    ^

    create or alter function f1 returns integer as
      declare ret integer;
    begin
      select n from v1 into ret;
      return ret;
    end
    ^

    create or alter procedure p1 returns (ret integer) as
    begin
      select n from v1 into ret;
    end
    ^
    set term ;^
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import time
#  import subprocess
#  import shutil
#  from subprocess import PIPE
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  this_db = db_conn.database_name
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
#  fdb_rest = os.path.join(context['temp_directory'],'tmp_6233_restored.fdb')
#  cleanup( (fdb_rest,) )
#
#  sql_init='''
#      set bail on;
#      create or alter procedure p1 as begin end;
#      create or alter function f1 returns integer as begin end;
#      commit;
#
#      set term ^;
#      create or alter view v1 as
#        select 1 as n from rdb$database
#      ^
#
#      create or alter function f1 returns integer as
#        declare ret integer;
#      begin
#        select n from v1 into ret;
#        return ret;
#      end
#      ^
#
#      create or alter procedure p1 returns (ret integer) as
#      begin
#        select n from v1 into ret;
#      end
#      ^
#      set term ;^
#      commit;
#
#  '''
#  runProgram('isql', [ dsn], sql_init)
#
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
#  p_sender = subprocess.Popen( [ context['gbak_path'], '-b', dsn, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ context['gbak_path'], '-c', 'stdin',  'localhost:' + fdb_rest ], stdin = p_sender.stdout, stdout = PIPE )
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#
#
#  sql_chk='''
#      set list on;
#      set count on;
#      select
#         RDB$DEPENDENT_NAME as dep_name
#        ,RDB$DEPENDED_ON_NAME as dep_on_name
#      from rdb$dependencies
#      order by 1,2;
#  '''
#
#  runProgram('isql',[ 'localhost:' + fdb_rest ], sql_chk)
#
#  cleanup( (fdb_rest,) )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

test_script_1 = """
    set list on;
    set count on;
    select
       RDB$DEPENDENT_NAME as dep_name
      ,RDB$DEPENDED_ON_NAME as dep_on_name
    from rdb$dependencies
    order by 1,2;
"""

expected_stdout_1 = """
    DEP_NAME                        F1
    DEP_ON_NAME                     V1
    DEP_NAME                        F1
    DEP_ON_NAME                     V1
    DEP_NAME                        P1
    DEP_ON_NAME                     V1
    DEP_NAME                        P1
    DEP_ON_NAME                     V1
    DEP_NAME                        V1
    DEP_ON_NAME                     RDB$DATABASE
    Records affected: 5
"""

fdb_restored = temp_file('core_6233_restored.fdb')

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action, fdb_restored: Path):
    with act_1.connect_server() as srv:
        backup = BytesIO()
        srv.database.local_backup(database=act_1.db.db_path, backup_stream=backup)
        backup.seek(0)
        srv.database.local_restore(database=fdb_restored, backup_stream=backup)
    #
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[act_1.get_dsn(fdb_restored)], input=test_script_1, connect_db=False)
    assert act_1.clean_stdout == act_1.clean_expected_stdout


