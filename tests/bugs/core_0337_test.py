#coding:utf-8
#
# id:           bugs.core_0337
# title:        bug #910430 ISQL and database dialect
# decription:
#               	::: NB :::
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_25.script
#
#                   When ISQL disconnects from database (either by dropping it or by trying to connect to
#                   non-existent database) is still remembers its sql dialect, which can lead to some
#                   inappropriate warning messages.
#
#                   Issue in original script: bug #910430 ISQL and database dialect
#                   Found in FB tracker as: http://tracker.firebirdsql.org/browse/CORE-337
#                   Fixed in 2.0 Beta 1
#
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#
# tracker_id:
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('CREATE DATABASE.*', 'CREATE DATABASE')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import sys
#  import subprocess
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
#
#  #--------------------------------------------
#
#  test_fdb=os.path.join(context['temp_directory'],'tmp_0337.fdb')
#
#  cleanup( test_fdb, )
#
#  db_conn.close()
#  sql='''
#      set echo on;
#
#      show sql dialect;
#
#      set sql dialect 1;
#
#      show sql dialect;
#
#      set sql dialect 3;
#
#      create database 'localhost:%(test_fdb)s' user '%(user_name)s' password '%(user_password)s';
#
#      show sql dialect;
#
#      drop database;
#
#      show database;
#
#      show sql dialect;
#
#      set sql dialect 1;
#  ''' % dict(globals(), **locals())
#
#  f_sql_chk = open( os.path.join(context['temp_directory'],'tmp_0337_ddl.sql'), 'w', buffering = 0)
#  f_sql_chk.write(sql)
#  flush_and_close( f_sql_chk )
#
#  f_sql_log = open( ''.join( (os.path.splitext(f_sql_chk.name)[0], '.log' ) ), 'w', buffering = 0)
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_sql_chk.name ], stdout = f_sql_log, stderr = subprocess.STDOUT)
#  flush_and_close( f_sql_log )
#
#  with open(f_sql_log.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( line.upper() )
#
#  cleanup( (test_fdb, f_sql_log.name, f_sql_chk.name) )
#
#
#---

expected_stdout_1 = """
    SHOW SQL DIALECT;
    Client SQL dialect has not been set and no database has been connected yet.

    SET SQL DIALECT 1;
    SHOW SQL DIALECT;
    Client SQL dialect is set to: 1. No database has been connected.

    SET SQL DIALECT 3;
    CREATE DATABASE 'LOCALHOST:C:\\FBTESTING\\QA\\FBT-REPO\\TMP2\\TMP_0337.FDB' USER 'SYSDBA' PASSWORD 'MASTERKEY';

    SHOW SQL DIALECT;
    Client SQL dialect is set to: 3 and database SQL dialect is: 3

    DROP DATABASE;

    SHOW DATABASE;

    SHOW SQL DIALECT;
    Client SQL dialect is set to: 3. No database has been connected.

    SET SQL DIALECT 1;
  """

expected_stderr_1 = """
Use CONNECT or CREATE DATABASE to specify a database
Use CONNECT or CREATE DATABASE to specify a database
Command error: SHOW DATABASE
"""

act_1 = isql_act('db_1', "", substitutions=substitutions_1)

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.db.drop()
    act_1.script = f"""
    SET ECHO ON;
    SHOW SQL DIALECT;
    SET SQL DIALECT 1;
    SHOW SQL DIALECT;
    SET SQL DIALECT 3;
    CREATE DATABASE '{act_1.db.dsn}' USER '{act_1.db.user}' PASSWORD '{act_1.db.password}';
    SHOW SQL DIALECT;
    DROP DATABASE;
    SHOW DATABASE;
    SHOW SQL DIALECT;
    SET SQL DIALECT 1;
    """
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute(do_not_connect=True)
    assert act_1.clean_expected_stdout == act_1.clean_stdout
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    act_1.db.create()



