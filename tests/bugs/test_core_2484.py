#coding:utf-8
#
# id:           bugs.core_2484
# title:        Success message when connecting to tiny trash database file
# decription:   
#                   We make invalid FDB file by creating binary file and write small data piece to it.
#                   Then we try to connect to such "database" using ISQL with passing trivial command
#                   like 'select current_timestamp' for execution.
#                   ISQL must raise error and quit (obviously without any result to STDOUT).
#               
#                   ::: NB :::
#                   If Windows with non-ascii language is used then message about overlapped IO
#                   ("-Overlapped I/O operation is in progress") will be translated by OS to localized
#                   text and it will be displayed in STDERR. This message must be suppressed or ignored.
#               
#                   Because of this, it was decided to redirect output of ISQL to logs and open
#                   them using codecs.open() with errors='ignore' option.
#                   We check presense of error message in STDERR file created by ISQL.
#                   It is ennough to verify that STDERR log contains pattern 'SQLSTATE = '.
#                   Checked on 4.0.0.2164; 3.0.7.33356
#               
#                   02-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#               
#                   NOTE: message that clearly points to the reason of failed connection is shown
#                   only on Linux FB 3.x:
#                   =====
#                    Statement failed, SQLSTATE = 08004
#                    file <...>/tmp_2484_fake.fdb is not a valid database
#                   =====
#               
#                   All other cases produce SQLSTATE = 08001 and somewhat strange after it (from my POV):
#                   =====
#                   Windows:
#                       I/O error during "ReadFile" operation for file "<...>\\TMP_2484_FAKE.FDB"
#                       -Error while trying to read from file
#               
#                   Linux:
#                       I/O error during "read_retry" operation for file "<...>/tmp_2484_fake.fdb"
#                       -Error while trying to read from file
#                       -Success <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< :-)
#                   =====
#               
#                   Checked on:
#                   * Windows: 4.0.0.2377, 3.0.8.33420 -- both on SS/CS
#                   * Linux:   4.0.0.2377, 3.0.8.33415
#               
#                
# tracker_id:   CORE-2484
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('SQLSTATE = 08004', 'SQLSTATE = 08001')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import codecs
#  import re
#  import time
#  
#  db_conn.close()
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#  f_fake_fdb = open( os.path.join(context['temp_directory'],'tmp_2484_fake.fdb'), 'wb')
#  f_fake_fdb.write('ŒåŁä')
#  flush_and_close( f_fake_fdb )
#  
#  f_fake_sql = open( os.path.splitext(f_fake_fdb.name)[0]+'.sql', 'w')
#  f_fake_sql.write('set heading off; select current_timestamp from rdb$database; quit;')
#  flush_and_close( f_fake_sql )
#  
#  f_fake_log = open( os.path.splitext(f_fake_fdb.name)[0]+'.log', 'w')
#  f_fake_err = open( os.path.splitext(f_fake_fdb.name)[0]+'.err', 'w')
#  subprocess.call( [ context['isql_path'], 'localhost:' + f_fake_fdb.name, "-i", f_fake_sql.name ],
#                   stdout = f_fake_log,
#                   stderr = f_fake_err
#                 )
#  flush_and_close( f_fake_log )
#  flush_and_close( f_fake_err )
#  
#  ###########################################################################
#  # Linux, FB 3.x:
#  #     Statement failed, SQLSTATE = 08004
#  #     file <...>/tmp_2484_fake.fdb is not a valid database
#  # Windows, FB 3.x:
#  # Statement failed, SQLSTATE = 08001
#  # I/O error during "ReadFile" operation for file "<...>\\TMP_2484_FAKE.FDB"
#  # -Error while trying to read from file
#  
#  # Linux, FB 4.x:
#  #     Statement failed, SQLSTATE = 08001
#  #     I/O error during "read_retry" operation for file "<...>/tmp_2484_fake.fdb"
#  #     -Error while trying to read from file
#  #     -Success
#  # Windows, FB 4.x:
#  # Statement failed, SQLSTATE = 08001
#  # I/O error during "ReadFile" operation for file "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\TMP_2484_FAKE.FDB"
#  # -Error while trying to read from file
#  # Overlapped I/O operation is in progress << WILL BE IN LOCALIZED FORM!
#  ###########################################################################
#  
#  p = re.compile('SQLSTATE\\s+=\\s+',re.IGNORECASE)
#  with codecs.open( filename = f_fake_err.name, mode = 'r', errors = 'ignore') as f:
#      for line in f:
#              if p.search(line):
#                          print(line)
#  
#  with codecs.open( filename = f_fake_log.name, mode = 'r', errors = 'ignore') as f:
#      for line in f:
#              if p.search(line):
#                          print('UNEXPECTED STDOUT: ' + line)
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( ( f_fake_fdb, f_fake_sql, f_fake_log, f_fake_err )  )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
        Statement failed, SQLSTATE = 08001
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_core_2484_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


