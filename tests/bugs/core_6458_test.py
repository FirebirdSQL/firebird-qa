#coding:utf-8
#
# id:           bugs.core_6458
# title:        Regression: Cancel Query function no longer works
# decription:
#                   We create .sql script with 'heavy query' that for sure will run more than several seconds.
#                   Then we launch asynchronous ISQL process to perform this query and take small pause for 1-2 second.
#                   After this we send signal CTRL_C_EVENT for emulating interruption that is done by pressing Ctrl-C.
#                   Then we wait for process finish (call wait() method) - this is necessary if ISQL will continue
#                   without interruprion (i.e. if something will be broken again).
#
#                   When method wait() will return control back, we can obtain info about whether child process was
#                   terminated or no (using method poll()). If yes (expected) then it must return 1.
#
#                   Finally, we check ISQL logs for STDOUT and STDERR. They must be as follows:
#                   * STDOUT -- must be empty
#                   * STDERR -- must contain (at least) two phrases:
#                       1. Statement failed, SQLSTATE = HY008
#                       2. operation was cancelled
#
#                   ::: NB :::
#                   Windows only: subprocess.Popen() must have argument: creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
#                   Otherwise we can not send signal Ctrl_C_EVENT to the child process.
#                   Linux: parameter 'creationflags' must be 0, signal.SIGINT is used instead of Ctrl_C_EVENT.
#
#                   See: https://docs.python.org/2.7/library/subprocess.html
#
#                   Confirmed bug on 4.0.0.2307: query could NOT be interrupted and we had to wait until it completed.
#                   Checked on 4.0.0.2324 (SS/CS): works OK, query can be interrupted via sending Ctrl-C signal.
#
#                   16.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                      Windows: 4.0.0.2422 SS/CS
#                      Linux:   4.0.0.2422 SS/CS
#
#
# tracker_id:   CORE-6458
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
import re
import signal
import subprocess
import time
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import platform
#  import subprocess
#  import signal
#  import datetime
#  import time
#  import re
#
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  FB_HOME = services.connect(host='localhost', user= user_name, password= user_password).get_home_directory()
#  FB_BINS = os.path.join( FB_HOME, 'bin'+os.sep if platform.system() == 'Linux' else '' )
#
#
#  #--------------------------------------------
#  def showtime():
#      global datetime
#      return ''.join( (datetime.datetime.now().strftime("%H:%M:%S.%f")[:11],'.') )
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
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#                  exit(1)
#  #-------------------------------------------------
#
#  f_sql_cmd = open( os.path.join(context['temp_directory'],'tmp-c6458.sql'),'w')
#  f_sql_cmd.write("set list on; select count(*) as LONG_QUERY_RESULT from (select 1 i from rdb$types a,rdb$types b,rdb$types c);")
#  flush_and_close( f_sql_cmd )
#
#  f_sql_log = open( os.path.splitext(f_sql_cmd.name)[0] + '.log','w')
#  f_sql_err = open( os.path.splitext(f_sql_cmd.name)[0] + '.err','w')
#
#  try:
#      # NB: subprocess.CREATE_NEW_PROCESS_GROUP is MANDATORY FOR SENDING CTRL_C SIGNAL on Windows:
#      p_flag = 0 if platform.system() == 'Linux' else subprocess.CREATE_NEW_PROCESS_GROUP
#      p_long = subprocess.Popen( [ os.path.join(FB_BINS, 'isql'), dsn, '-q', '-i', f_sql_cmd.name]
#                                 ,stdout=f_sql_log
#                                 ,stderr=f_sql_err
#                                 ,creationflags = p_flag
#                               )
#      time.sleep(1)
#      p_long.send_signal( signal.SIGINT if platform.system() == 'Linux' else signal.CTRL_C_EVENT )
#      p_long.wait()
#      print('Was ISQL process terminated ? => ', p_long.poll())
#  except Exception,e:
#      print(e)
#  finally:
#      flush_and_close( f_sql_log )
#      flush_and_close( f_sql_err )
#  #--------------------------------------------------
#
#  with open(f_sql_log.name) as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED STDOUT: ', line)
#
#  allowed_patterns = (
#       re.compile('.*SQLSTATE\\s+=\\s+HY008', re.IGNORECASE)
#      ,re.compile('operation\\s+(was\\s+)?cancelled', re.IGNORECASE)
#  )
#
#  with open(f_sql_err.name) as f:
#      for line in f:
#          if line.split():
#              match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#              if match2some:
#                  print( (' '.join(line.split()).lower()) )
#
#  # cleanup
#  #########
#  time.sleep(1)
#  cleanup( [ i.name for i in (f_sql_cmd, f_sql_log, f_sql_err) ] )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Was ISQL process terminated ? =>  1
    statement failed, sqlstate = hy008
    operation was cancelled
"""

heavy_script_1 = temp_file('heavy_script.sql')
heavy_stdout_1 = temp_file('heavy_script.out')
heavy_stderr_1 = temp_file('heavy_script.err')

@pytest.mark.version('>=4.0')
def test_1(act_1: Action, heavy_script_1: Path, heavy_stdout_1: Path, heavy_stderr_1: Path,
           capsys):
    heavy_script_1.write_text("set list on; select count(*) as LONG_QUERY_RESULT from (select 1 i from rdb$types a,rdb$types b,rdb$types c);")
    with open(heavy_stdout_1, mode='w') as heavy_out, open(heavy_stderr_1, mode='w') as heavy_err:
        # NB: subprocess.CREATE_NEW_PROCESS_GROUP is MANDATORY FOR SENDING CTRL_C SIGNAL on Windows
        flags = 0 if act_1.platform == 'Linux' else subprocess.CREATE_NEW_PROCESS_GROUP
        p_heavy_sql = subprocess.Popen([act_1.vars['isql'], '-i', str(heavy_script_1),
                                        '-user', act_1.db.user,
                                       '-password', act_1.db.password, act_1.db.dsn],
                                       stdout=heavy_out, stderr=heavy_err,
                                       creationflags=flags)
        try:
            time.sleep(4)
            p_heavy_sql.send_signal(signal.SIGINT if act_1.platform == 'Linux' else signal.CTRL_C_EVENT)
            p_heavy_sql.wait()
            print('Was ISQL process terminated ? => ', p_heavy_sql.poll())
        except Exception as e:
            print(e)
    #
    for line in heavy_stdout_1.read_text().splitlines():
        if line.split():
            print('UNEXPECTED STDOUT: ', line)
    allowed_patterns = [re.compile('.*SQLSTATE\\s+=\\s+HY008', re.IGNORECASE),
                        re.compile('operation\\s+(was\\s+)?cancelled', re.IGNORECASE)]
    for line in heavy_stderr_1.read_text().splitlines():
        if line.split():
            if act_1.match_any(line, allowed_patterns):
                print(' '.join(line.split()).lower())
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
