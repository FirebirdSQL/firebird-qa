#coding:utf-8
#
# id:           bugs.core_6040
# title:        Metadata script extracted using ISQL is invalid/incorrect when table has COMPUTED BY field
# decription:   
#                   Confirmed bug on 3.0.5.33118, 4.0.0.1485
#                   NB: 'collate' clause must present in DDL of computed_by field, otherwise extracted metadata script will be correct.
#               
#                   Checked on:
#                       4.0.0.1487: OK, 3.674s.
#                       3.0.5.33120: OK, 2.622s.
#               
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
#                
# tracker_id:   CORE-6040
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  import fdb
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
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            print('type(f_names_list[i])=',type(f_names_list[i]))
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  tmpfdb='$(DATABASE_LOCATION)'+'tmp_core_6040.fdb'
#  
#  cleanup( (tmpfdb,) )
#  
#  con = fdb.create_database( dsn = 'localhost:'+tmpfdb, charset = 'win1252' )
#  con.close()
#  con=fdb.connect( dsn = 'localhost:'+tmpfdb )
#  
#  sql_ddl='''
#      recreate table users (
#          f01 varchar(32) character set win1252 not null collate win_ptbr
#          ,f02 computed by ( f01 collate win_ptbr )
#      )
#  '''
#  con.execute_immediate(sql_ddl)
#  con.commit()
#  
#  f_meta_sql = open( os.path.join(context['temp_directory'],'tmp_meta_6040.sql'), 'w')
#  f_meta_err = open( os.path.join(context['temp_directory'],'tmp_meta_6040.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], "-x", "-ch", "win1252", 'localhost:'+tmpfdb],
#                   stdout = f_meta_sql,
#                   stderr = f_meta_err
#                 )
#  
#  flush_and_close( f_meta_sql )
#  flush_and_close( f_meta_err )
#  
#  con.execute_immediate('drop table users')
#  con.commit()
#  con.close()
#  
#  f_apply_log = open( os.path.join(context['temp_directory'],'tmp_apply_6040.log'), 'w')
#  f_apply_err = open( os.path.join(context['temp_directory'],'tmp_apply_6040.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], "-ch", "win1252", 'localhost:'+tmpfdb, "-i", f_meta_sql.name ],
#                   stdout = f_apply_log,
#                   stderr = f_apply_err
#                 )
#  
#  flush_and_close( f_apply_log )
#  flush_and_close( f_apply_err )
#  
#  with open( f_meta_err.name,'r') as f:
#      for line in f:
#          print("METADATA EXTRACTION PROBLEM, STDERR: "+line)
#  
#  with open( f_apply_log.name,'r') as f:
#      for line in f:
#          print("METADATA APPLYING PROBLEM, STDOUT: "+line)
#  
#  with open( f_apply_err.name,'r') as f:
#      for line in f:
#          print("METADATA APPLYING PROBLEM, STDERR: "+line)
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_meta_sql, f_meta_err, f_apply_log, f_apply_err, tmpfdb, ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


