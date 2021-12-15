#coding:utf-8
#
# id:           bugs.core_6437
# title:        gfix cannot set big value for buffers
# decription:
#                   New database must be created in THIS code rather than "outside" (in fbtest) for reproducing bug.
#                   Confirmed bug on 4.0.0.2225.
#                   Checked on Windows:
#                       4.0.0.2249 SS: 3.284s.
#                       3.0.2.32703 SS: 2.645s.
#                       3.0.7.33387 SS: 3.301s.
#                       3.0.6.33328 CS: 6.145s.
#
#                   ::: NB :::
#                   On build 4.0.0.2225 attempt to change buffers via gfix failed when value was >= 524337 for DB with page_size=8192.
#                   Perhaps this was related to allocating memory more than 2Gb plus small addition (exact value: 2.00018692 Gb).
#                   Ouput of gfix in this case contained:
#                   =======
#                     I/O error during "ReadFile" operation for file "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\TMP_GFIX_6437.FDB"
#                     -Error while trying to read from file
#                     -Invalid attempt to access memory address << localized message!
#                   =======
#                   Test creates database with page size = 8192 and tries to run 'gfix -buffers 524337', with further checking that:
#                   * output of gfix is empty;
#                   * page buffers has been changed and equals to this new value.
#
#                   DO NOT change this value to some "really too big" value otherwise it will fail with "unable to allocate memory"!
#                   Checked again (15.03.2021) on:
#                       * Windows: 4.0.0.2387, 3.0.8.33426
#                       * Linux:   4.0.0.2387, 3.0.8.33426
#
# tracker_id:   CORE-6437
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 3.0.8
# resources: None

substitutions_1 = [('^((?!(File|file|Page buffers)|(Page size)).)*$', ''), ('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import subprocess
#  from fdb import services
#  import time
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
#  db_name = os.path.join(context['temp_directory'],'tmp_gfix_6437.fdb')
#
#  cleanup( (db_name,) )
#
#  runProgram('isql',[ '-q' ], "create database '%(db_name)s' page_size 8192;" % locals())
#
#  f_run_log=open( os.path.join(context['temp_directory'],'tmp_gfix_6437.log'), 'w')
#  subprocess.call( [ context['gfix_path'], db_name, "-buffers", "524337" ], stdout=f_run_log, stderr=subprocess.STDOUT )
#  flush_and_close(f_run_log)
#
#  time.sleep(1)
#  with open(f_run_log.name,'r') as f:
#      for line in f:
#          print('UNEXPECTED GFIX OUTPUT: ' + line)
#
#  runProgram('gstat',[ '-h', db_name ])
#
#  cleanup( (db_name, f_run_log,) )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Page size 8192
    Page buffers 524337
"""

test_db = temp_file('tmp_gfix_6437.fdb')

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action, test_db: Path):
    act_1.isql(switches=['-q'], connect_db=False,
               input=f"create database '{test_db}' page_size 8192;")
    #
    act_1.reset()
    act_1.gfix(switches=[str(test_db), '-buffers', '524337'])
    act_1.reset()
    #
    act_1.expected_stdout = expected_stdout_1
    act_1.gstat(switches=['-h', str(test_db)], connect_db=False)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
