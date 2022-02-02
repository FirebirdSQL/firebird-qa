#coding:utf-8

"""
ID:          issue-3438
ISSUE:       3438
TITLE:       New generators are created with wrong value when more than 32K generators was previously created
DESCRIPTION:
  Confirmed bug on 2.5.0.26074:
  sequence 'g_1' that is created after <TOTAL_SEQUENCES_COUNT> iterations
  has current value = 59049 (instead of expected 0).
NOTES:
  Re-implemented in order to generate SQL script with more than 32K create / get gen_id / drop sequences.
  Total number of created sequences is set by 'TOTAL_SEQUENCES_COUNT' variable.
JIRA:        CORE-3058
FBTEST:      bugs.core_3058
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout_1 = """
    MON$FORCED_WRITES               0
    GEN_ID                          0
"""

TOTAL_SEQUENCES_COUNT = 33000

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# test_script_1
#---
#
#
#  import os
#  import subprocess
#  import time
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_name = db_conn.database_name
#  db_conn.close()
#  runProgram('gfix',[dsn,'-w','async'])
#
#  ###########################
#  TOTAL_SEQUENCES_COUNT=33000
#  ###########################
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
#
#  script='''
#      set bail on;
#      set list on;
#      select mon$forced_writes from mon$database;
#      set term #;
#  '''
#
#  for i in range(1,TOTAL_SEQUENCES_COUNT+1):
#      script = '\\n'.join(
#                            (  script
#                              ,'create sequence g_%d#' % i
#                              ,'execute block as declare c int; begin c = gen_id(g_%d, %d); end#' % (i, i**2)
#                              ,'drop sequence g_%d#' % i
#                            )
#                         )
#
#  script = '\\n'.join(
#                        (   script
#                           ,'set term ;#'
#                           ,'create sequence g_%d;' % 1
#                           ,'commit;'
#                           ,'select gen_id(g_1,0) from rdb$database;'
#                        )
#                    )
#
#
#  f_isql_cmd=open(os.path.join(context['temp_directory'],'tmp_core_3058.sql'), 'w')
#  f_isql_cmd.write(script)
#  flush_and_close( f_isql_cmd )
#
#  f_isql_log=open(os.path.join(context['temp_directory'],'tmp_core_3058.log'),'w')
#  f_isql_err=open(os.path.join(context['temp_directory'],'tmp_core_3058.err'),'w')
#
#  # NB: use local connection here in order to increase speed:
#  subprocess.call([ context['isql_path'], db_name, "-i", f_isql_cmd.name],stdout = f_isql_log, stderr = f_isql_err)
#
#  flush_and_close( f_isql_log )
#  flush_and_close( f_isql_err )
#
#  with open(f_isql_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print('UNEXPECTED STDERR: ' + line.strip())
#
#  with open(f_isql_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print(line.strip())
#
#
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup((f_isql_cmd, f_isql_log, f_isql_err))
#---
