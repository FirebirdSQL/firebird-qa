#coding:utf-8
#
# id:           bugs.core_2788
# title:        isql extracts the array dimensions after the character set name
# decription:
#
# tracker_id:   CORE-2788
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('- line .*', ''), ('At line .*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  #---------------------------------------------
#
#  def flush_and_close(file_handle):
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
#
#  #--------------------------------------------
#
#  sql_ddl='''    create domain dm_test as char(1) character set iso8859_1[1:2];
#      create domain dm_test as char(1)[1:2] character set iso8859_1;
#      commit;
#      show domain dm_test;
#  '''
#
#
#  f_init_sql = open( os.path.join(context['temp_directory'],'tmp_init_2788.sql'), 'w')
#  f_init_sql.write(sql_ddl)
#  flush_and_close( f_init_sql )
#
#  f_init_log = open( os.path.join(context['temp_directory'],'tmp_init_2788.log'), 'w')
#  f_init_err = open( os.path.join(context['temp_directory'],'tmp_init_2788.err'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-i", f_init_sql.name],
#                   stdout = f_init_log,
#                   stderr = f_init_err
#                 )
#  # This file should be empty:
#  flush_and_close( f_init_log )
#
#  # This file should contain error messages about 1st 'CREATE DOMAIN' statement that has syntax trouble:
#  flush_and_close( f_init_err )
#
#  # This file should contain error messages about 1st 'CREATE DOMAIN' statement that has syntax trouble:
#  with open( f_init_err.name,'r') as f:
#     print(f.read())
#
#
#  f_xmeta_log = open( os.path.join(context['temp_directory'],'tmp_xmeta_2788.log'), 'w')
#  f_xmeta_err = open( os.path.join(context['temp_directory'],'tmp_xmeta_2788.err'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-x"], stdout = f_xmeta_log, stderr = f_xmeta_err)
#
#  # This file should contain metadata - domain definition:
#  flush_and_close( f_xmeta_log )
#
#  # This file should be empty:
#  flush_and_close( f_xmeta_err )
#
#  att1 = fdb.connect(dsn=dsn.encode())
#  cur1=att1.cursor()
#  cur1.execute("drop domain dm_test")
#  att1.commit()
#
#  att1.close()
#
#  # This shoudl issue "There is no domain DM_TEST in this database":
#  runProgram('isql',[dsn, '-q'],'show domain dm_test;')
#
#  f_apply_log = open( os.path.join(context['temp_directory'],'tmp_apply_2788.log'), 'w')
#  f_apply_err = open( os.path.join(context['temp_directory'],'tmp_apply_2788.err'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-i", f_xmeta_log.name],
#                   stdout = f_apply_log,
#                   stderr = f_apply_err
#                 )
#  # Both of these files should be empty:
#  flush_and_close( f_apply_log )
#  flush_and_close( f_apply_err )
#
#  # This shoudl issue DDL of just created domain:
#  runProgram('isql',[dsn, '-q'],'show domain dm_test;')
#
#  # No output should be here:
#  with open( f_xmeta_err.name,'r') as f:
#     print(f.read())
#
#  # No output should be here:
#  with open( f_apply_log.name,'r') as f:
#     print(f.read())
#
#
#  # No output should be here:
#  with open( f_apply_err.name,'r') as f:
#     print(f.read())
#
#
#  ################################################
#  # Cleanup
#  time.sleep(1)
#  cleanup( [i.name for i in (f_init_sql,f_init_log,f_init_err,f_xmeta_log,f_xmeta_err,f_apply_log,f_apply_err) ] )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    DM_TEST                         ARRAY OF [2]
    CHAR(1) CHARACTER SET ISO8859_1 Nullable
"""

expected_stderr_1_a = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 57
    -[
"""

expected_stderr_1_b = """
   There is no domain DM_TEST in this database
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    sql_ddl = '''    create domain dm_test as char(1) character set iso8859_1[1:2];
        create domain dm_test as char(1)[1:2] character set iso8859_1;
        commit;
        show domain dm_test;
    '''
    act_1.expected_stderr = expected_stderr_1_a
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[], input=sql_ddl)
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout
    #
    act_1.reset()
    act_1.isql(switches=['-x'])
    xmeta = act_1.stdout
    #
    with act_1.db.connect() as con:
        c = con.cursor()
        c.execute('drop domain dm_test')
        con.commit()
    #
    act_1.reset()
    act_1.expected_stderr = expected_stderr_1_b
    act_1.isql(switches=['-q'], input='show domain dm_test;')
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    #
    act_1.reset()
    act_1.isql(switches=[], input=xmeta)
    #
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q'], input='show domain dm_test;')
    assert act_1.clean_stdout == act_1.clean_expected_stdout
