#coding:utf-8
#
# id:           bugs.core_5078
# title:        "Invalid BLOB ID" error
# decription:
#                  Confirmed, got exception during selecting data on Classic WI-V2.5.5.26952, x64.
#                  STDERR:
#                      Statement failed, SQLSTATE = 42000
#                      invalid BLOB ID
#                      -At procedure 'DO_CHANGETXSTATUS' line: 31, col: 21
#                  Last record in STDOUT:
#                      INFO                            inserting blob
#                      UPDCNT                          51
#                      TRANS                           1361600
#                      SUBS                            2806
#                      MSGTYPE                         2524
#                      NOTIFYPARAMS                    1482
#
# tracker_id:   CORE-5078
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from pathlib import Path
import zipfile
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import subprocess
#  from subprocess import Popen
#  import zipfile
#  import time
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_5078.zip') )
#  zf.extractall( context['temp_directory'] )
#  zf.close()
#
#  # Result: file tmp_core_5078.fbk is extracted into context['temp_directory']
#
#  tmp_fbk=os.path.join(context['temp_directory'],'tmp_core_5078.fbk')
#  tmp_fdb=os.path.join(context['temp_directory'],'tmp_core_5078.fdb')
#
#  cleanup( (tmp_fdb,) )
#
#  # Restoring from .fbk:
#  runProgram( context['fbsvcmgr_path'],['localhost:service_mgr','action_restore','dbname',tmp_fdb,'bkp_file',tmp_fbk])
#
#  f_sql=open( os.path.join(context['temp_directory'],'tmp_isql_5078.sql'), 'w')
#  f_sql.write('set list on; select * from do_changeTxStatus;')
#  flush_and_close( f_sql )
#
#  f_log = open(os.devnull, 'w')
#  f_err = open( os.path.join(context['temp_directory'],'tmp_isql_5078.err'), 'w')
#
#  subprocess.call( [context['isql_path'], 'localhost:'+tmp_fdb, "-i", f_sql.name],stdout=f_log,stderr=f_err)
#
#  flush_and_close( f_log )
#  flush_and_close( f_err )
#
#  time.sleep(1)
#
#  # This file should be EMPTY:
#  ###########################
#  with open(f_err.name) as f:
#    print( f.read() )
#
#  # CLEANUP
#  ##########
#  time.sleep(1)
#  cleanup( (tmp_fbk, tmp_fdb, f_err, f_sql) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

fbk_file_1 = temp_file('tmp_core_5078.fbk')
fdb_file_1 = temp_file('tmp_core_5078.fdb')

@pytest.mark.version('>=2.5.6')
def test_1(act_1: Action, fbk_file_1: Path, fdb_file_1: Path):
    zipped_fbk_file = zipfile.Path(act_1.files_dir / 'core_5078.zip',
                    at='tmp_core_5078.fbk')
    fbk_file_1.write_bytes(zipped_fbk_file.read_bytes())
    with act_1.connect_server() as srv:
        srv.database.restore(database=fdb_file_1, backup=fbk_file_1)
        srv.wait()
    # This should execute without errors
    act_1.isql(switches=[str(fdb_file_1)], input='set list on; select * from do_changeTxStatus;',
               connect_db=False)
