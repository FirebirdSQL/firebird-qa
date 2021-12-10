#coding:utf-8
#
# id:           bugs.core_6023
# title:        FB4 unable to overwrite older ods database
# decription:
#                   Database (employee.fdb) with ODS 11.2 has been compressed to .zip and stored in {FBT_REPO}/files subdirectory.
#                   Test unpacks this .fdb and:
#                       1) tries to print its header (using gstat -h) - it must fail with "Wrong ODS version, expected NN, encountered 11"
#                          (where <NN> is ODS major number that is supported by current FB version);
#                       2) makes attempt to replace this .fdb by following action:
#                           <current_FB>/gbak -b <dsn> stdout | <current_FB>/gbak -rep stdin <fdb_with_ODS_11_2>
#                       3) tries to make connection to just restored DB and write result.
#
#                   If replacement was successfull then connection *must* be estabished and it is enough to print SIGN(current_connection).
#                   Outcome of this ("1") means that all completed OK.
#
#                   Confirmed bug on 4.0.0.1803: attempt to restore fails with:
#                       gbak: ERROR:unsupported on-disk structure for file ...; found 11.2, support 13.0
#                       gbak: ERROR:    IProvider::attachDatabase failed when loading mapping cache
#                       gbak: ERROR:failed to create database localhost:...
#                       gbak:Exiting before completion due to errors
#
#                   ::: CAUTION :::
#                   DO NOT try to run this test on any other FB build just after check build 4.0.0.1803!
#                   One need to STOP instance 4.0.0.1803 before this or wait for at least 130 seconds,
#                   otherwise checked FB will crash. Problem relates to shmem-files in C:\\ProgramData
#               irebird\\.
#                   This problem has the same nature that is described in CORE-6476.
#                   See letter to Vlad et al 16.02.2021 09:02
#                   ("Crash of 4.0.0.2365 when attempt to get server version just after doing the same on 4.0.0.1803")
#                   :::::::::::::::
#
#                   Checked on 4.0.0.2365 - all OK.
#
# tracker_id:   CORE-6023
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
import zipfile
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('expected [\\d]+', 'expected NN')]

init_script_1 = """"""

# Database is extracted from zip
db_1 = db_factory(sql_dialect=3, init=init_script_1)


# test_script_1
#---
#
#  import os
#  import sys
#  import zipfile
#  import time
#  import subprocess
#  from subprocess import PIPE
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#
#  #--------------------------------------------
#  #print(db_conn.firebird_version)
#  db_conn.close()
#
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_6023-ods-11_2-fdb.zip') )
#  tmp_fdb_to_replace = os.path.join( '$(DATABASE_LOCATION)', 'core_6023-ods-11_2.fdb' )
#
#  zf.extract( os.path.split(tmp_fdb_to_replace)[1], '$(DATABASE_LOCATION)')
#  zf.close()
#
#  # Ensure that we really have deal with .fdb file with old ODS.
#  # Must issue: "Wrong ODS version, expected 13, encountered 11":
#  runProgram('gstat',['-h', tmp_fdb_to_replace])
#
#  f_restore_with_replace=open( os.path.join(context['temp_directory'],'tmp_6023_rep.err'), 'w')
#
#  p_sender = subprocess.Popen( [ context['gbak_path'], '-b', dsn, 'stdout' ], stdout=PIPE)
#  p_getter = subprocess.Popen( [ context['gbak_path'], '-rep', 'stdin',  'localhost:' + os.path.join( '$(DATABASE_LOCATION)', tmp_fdb_to_replace ) ], stdin = p_sender.stdout, stdout = PIPE, stderr = f_restore_with_replace)
#  p_sender.stdout.close()
#  p_getter_stdout, p_getter_stderr = p_getter.communicate()
#
#  flush_and_close(f_restore_with_replace)
#
#  with open(f_restore_with_replace.name) as f:
#      for line in f:
#          print('UNEXPECTED STDERR: '+line)
#
#
#  runProgram( 'isql',['-q', 'localhost:' + os.path.join( '$(DATABASE_LOCATION)', tmp_fdb_to_replace )], 'set list on; select sign(current_connection) as restore_with_replace_result from rdb$database;' )
#
#  cleanup( (tmp_fdb_to_replace, f_restore_with_replace.name) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    RESTORE_WITH_REPLACE_RESULT     1
"""

expected_stderr_1 = """
    Wrong ODS version, expected 13, encountered 11
"""

fdb_112_file = temp_file('core_6023-ods-11_2.fdb')
fbk_file = temp_file('core_6023.fbk')

@pytest.mark.version('>=4.0')
def test_1(act_1: Action, fdb_112_file: Path, fbk_file: Path):
    zipped_fdb_file = zipfile.Path(act_1.vars['files'] / 'core_6023-ods-11_2-fdb.zip',
                                   at='core_6023-ods-11_2.fdb')
    fdb_112_file.write_bytes(zipped_fdb_file.read_bytes())
    # Change permissions
    fdb_112_file.chmod(16895)
    # Ensure that we really have deal with .fdb file with old ODS.
    act_1.expected_stderr = expected_stderr_1
    act_1.gstat(switches=['-h', str(fdb_112_file)], connect_db=False)
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    # Backup work database and restore over extracted db
    act_1.reset()
    act_1.gbak(switches=['-b', act_1.db.dsn, str(fbk_file)])
    act_1.reset()
    act_1.gbak(switches=['-rep', str(fbk_file), f'localhost:{fdb_112_file}'])
    #
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q', f'localhost:{fdb_112_file}'], connect_db=False,
               input='set list on; select sign(current_connection) as restore_with_replace_result from rdb$database;')
    assert act_1.clean_stdout == act_1.clean_expected_stdout
