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
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SHOW SQL DIALECT;
    CLIENT SQL DIALECT HAS NOT BEEN SET AND NO DATABASE HAS BEEN CONNECTED YET.

    SET SQL DIALECT 1;
    SHOW SQL DIALECT;
    CLIENT SQL DIALECT IS SET TO: 1. NO DATABASE HAS BEEN CONNECTED.

    SET SQL DIALECT 3;
    CREATE DATABASE 'LOCALHOST:C:\\FBTESTING\\QA\\FBT-REPO\\TMP2\\TMP_0337.FDB' USER 'SYSDBA' PASSWORD 'MASTERKEY';

    SHOW SQL DIALECT;
    CLIENT SQL DIALECT IS SET TO: 3 AND DATABASE SQL DIALECT IS: 3

    DROP DATABASE;
    
    SHOW DATABASE;
    COMMAND ERROR: SHOW DATABASE

    SHOW SQL DIALECT;
    CLIENT SQL DIALECT IS SET TO: 3. NO DATABASE HAS BEEN CONNECTED.

    SET SQL DIALECT 1;
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


