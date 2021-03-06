#coding:utf-8
#
# id:           bugs.core_5737
# title:         Invalid parameters of gds transaction in ISQL
# decription:   
#                   ISQL hangs when trying to show various system objects in a case when other attachment has uncommitted changes to that objects
#                   We create (in Python connection) one table TEST1 with PK and commit transaction.
#                   Then we create second (similar) table TEST2 but do not commit transaction.
#                   After this we launch ISQL in async. mode and ask him to perform SHOW TABLE and SHOW INDEX commands.
#                   ISQL:
#                   1) should NOT hang (it did this because of launching Tx in read committed NO record_version);
#                   2) should output only info about table TEST1 and ints PK index.
#                   3) should not output any info about non-committed DDL of table TEST2.
#               
#                   Confirmed bug on 3.0.3.32837 and 4.0.0.800 (ISQL did hang when issued any of 'SHOW TABLE' / 'SHOW INDEX' copmmand).
#                   Checked on:
#                       3.0.3.32901: OK, 3.938s.
#                       4.0.0.875: OK, 3.969s.
#                
# tracker_id:   CORE-5737
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  from subprocess import Popen
#  import time
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
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
#  cur = db_conn.cursor()
#  db_conn.execute_immediate('recreate table test1(id int primary key using descending index test1_id_pk_desc)')
#  db_conn.commit()
#  cur.execute('recreate table test2(id int primary key using descending index test2_id_pk_desc)')
#  
#  show_query='''
#      show table;
#      show index;
#  '''
#  
#  f_show_command_sql = open( os.path.join(context['temp_directory'],'tmp_local_host_5737.sql'), 'w')
#  f_show_command_sql.write( show_query )
#  flush_and_close( f_show_command_sql )
#  
#  f_show_command_log = open( os.path.join(context['temp_directory'],'tmp_local_host_5737.log'), 'w')
#  f_show_command_err = open( os.path.join(context['temp_directory'],'tmp_local_host_5737.err'), 'w')
#  
#  # WARNING: we launch ISQL here in async mode in order to have ability to kill its process if it will hang!
#  ############################################
#  p_isql_to_local_host = subprocess.Popen( [ context['isql_path'], dsn, "-i", f_show_command_sql.name ],
#                   stdout = f_show_command_log,
#                   stderr = f_show_command_err
#                 )
#  
#  time.sleep(2)
#  
#  p_isql_to_local_host.terminate()
#  flush_and_close( f_show_command_log )
#  flush_and_close( f_show_command_err )
#  
#  with open( f_show_command_log.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('STDOUT: ', ' '.join(line.split()) )
#  
#  
#  with open( f_show_command_err.name,'r') as f:
#    for line in f:
#        if line.split():
#          print('STDERR: ', ' '.join(line.split()) )
#  
#  cur.close()
#  
#  
#  # Cleanup.
#  ##########
#  time.sleep(1)
#  cleanup( (f_show_command_sql, f_show_command_log, f_show_command_err) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STDOUT:  TEST1
    STDOUT:  TEST1_ID_PK_DESC UNIQUE DESCENDING INDEX ON TEST1(ID)
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


