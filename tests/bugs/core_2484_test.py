#coding:utf-8

"""
ID:          issue-2897
ISSUE:       2897
TITLE:       Success message when connecting to tiny trash database file
DESCRIPTION:
  We make invalid FDB file by creating binary file and write small string in it (text: 'ŒåŁä').
  Then we try to connect to such "database" using ISQL with passing trivial command
  like 'select current_timestamp' for execution.
  ISQL must raise error and quit (obviously without any result to STDOUT).

  STDERR differs dependign on OS.
  First line in error message is the same on Windows and Linux: "Statement failed, SQLSTATE = 08001",
  but starting from 2nd line messages differ:
  1) Windows:
    I/O error during "ReadFile" operation for file "..."
    -Error while trying to read from file
  2) Linux:
    I/O error during "read" operation for file "..."
    -File size is less than expected

  ::: NOTE ABOUT WINDOWS :::
  On Windows additional message did appear at last line, and it could be in localized form:
  -Overlapped I/O operation is in progress
  (only FB 4.0.x and 5.0.x were affected; NO such problem with FB 3.x)

  This has been considered as bug (see letter from Vlad, 16.09.2021 10:16, subject: "What to do with test for CORE-2484"),
  but if we want to check for presence of this message then we have to use codecs.open() invocation with suppressing
  with encoding = 'ascii' and suppressing non-writeable characters by specifying: errors = 'ignore'
  This bug was fixed long after time when this test was implemented:
    1) v4.0-release: fixed 19.09.2021 17:22, commit:
       https://github.com/FirebirdSQL/firebird/commit/54a2d5a39407b9d65b3f2b7ad614c3fc49abaa88
    2) refs/heads/master: fixed 19.09.2021 17:24, commit:
       https://github.com/FirebirdSQL/firebird/commit/90e1da6956f1c5c16a34d2704fafb92383212f37
NOTES: Related issues.
[18.03.2021] https://github.com/FirebirdSQL/firebird/issues/6747
  ("Wrong message when connecting to tiny trash database file", ex. CORE-6518)
[31.03.2021] https://github.com/FirebirdSQL/firebird/issues/6755
  ("Connect to database that contains broken pages can lead to FB crash", ex. CORE-6528)
[14.09.2021] https://github.com/FirebirdSQL/firebird/issues/6968
  ("On Windows, engine may hung when works with corrupted database and read after the end of file")
JIRA:        CORE-2484
"""

import pytest
from firebird.qa import *

substitutions = [('SQLSTATE = 08004', 'SQLSTATE = 08001'),
                 ('operation for file .*', 'operation for file'),
                 ('STDERR: After line \\d+ in file.*', 'STDERR: After line in file')]

db = db_factory(charset='UTF8')

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
#  subprocess.call( [ context['isql_path'], 'localhost:' + f_fake_fdb.name, "-q", "-i", f_fake_sql.name ],
#                   stdout = f_fake_log,
#                   stderr = f_fake_err
#                 )
#  flush_and_close( f_fake_log )
#  flush_and_close( f_fake_err )
#
#  ###########################################################################
#  # Windows, FB 3.x:
#  # Statement failed, SQLSTATE = 08001
#  # I/O error during "ReadFile" operation for file "<...>\\TMP_2484_FAKE.FDB"
#  # -Error while trying to read from file
#
#  # Windows, FB 4.x:
#  # Statement failed, SQLSTATE = 08001
#  # I/O error during "ReadFile" operation for file "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\TMP_2484_FAKE.FDB"
#  # -Error while trying to read from file
#  # Overlapped I/O operation is in progress << WILL BE IN LOCALIZED FORM!
#  ###########################################################################
#
#  for x in (f_fake_err, f_fake_log):
#      with codecs.open( filename = x.name, mode = 'r', encoding = 'ascii', errors = 'ignore') as f:
#          for line in f:
#              if line.split():
#                  print( ('STDOUT: ' if x == f_fake_log else 'STDERR: ') + line )
#
#  '''
#  p = re.compile('SQLSTATE\\s+=\\s+',re.IGNORECASE)
#  with codecs.open( filename = f_fake_err.name, mode = 'r', errors = 'replace') as f:
#      for line in f:
#          if p.search(line):
#              print(line)
#
#  with codecs.open( filename = f_fake_log.name, mode = 'r', errors = 'replace') as f:
#      for line in f:
#          if p.search(line):
#              print('UNEXPECTED STDOUT: ' + line)
#  '''
#
#  # cleanup:
#  ##########
#  time.sleep(1)
#  #cleanup( ( f_fake_fdb, f_fake_sql, f_fake_log, f_fake_err )  )
#
#---

act = python_act('db', substitutions=substitutions)

expected_stdout = """
    STDERR: Statement failed, SQLSTATE = 08001
    STDERR: I/O error during "ReadFile" operation for file "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\TMP_2484_FAKE.FDB"
    STDERR: -Error while trying to read from file
    STDERR: After line in file
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3.0')
def test_1():
    pytest.fail("Not IMPLEMENTED")
