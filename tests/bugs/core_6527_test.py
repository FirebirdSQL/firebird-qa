#coding:utf-8
#
# id:           bugs.core_6527
# title:        Regression: inline comment of SP parameter with closing parenthesis leads to incorrect SQL when trying to extract metadata
# decription:   
#                   Confirmed bug on 4.0.0.2394, 3.0.8.33426
#                   Checked on 4.0.0.2401, 3.0.8.33435 -- all OK.
#                
# tracker_id:   CORE-6527
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import shutil
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  this_fdb = db_conn.database_name
#  temp_fdb = os.path.join( '$(DATABASE_LOCATION)', 'tmp_core_6527.tmp' )
#  db_conn.close()
#  
#  shutil.copy(this_fdb, temp_fdb)
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
#  sql_ddl='''
#      set term ^;
#      create or alter procedure sp_test(
#          a_base_doc_id int,
#          a_base_doc_oper_id int default null -- (one of parameters to standalone procedure)
#      )
#      as
#          declare v_info varchar(100);
#      begin
#  
#          v_info = 'base_doc='||a_base_doc_id;
#      end
#      ^
#      create or alter function fn_test(
#          a_base_doc_id int,
#          a_base_doc_oper_id int default null -- (one of parameters to standalone function)
#      )
#      returns int
#      as
#          declare v_info varchar(100);
#      begin
#  
#          v_info = 'base_doc='||a_base_doc_id;
#          return 1;
#      end
#      ^
#  
#      create or alter package pg_test as
#      begin
#          procedure sp_test(
#              a_base_doc_id int,
#              a_base_doc_oper_id int default null -- (one of parameters to packaged procedure)
#          );
#          function fn_test(
#              a_base_doc_id int,
#              a_base_doc_oper_id int default null -- (one of parameters to packaged procedure)
#          ) returns int;
#      end
#      ^
#      recreate package body pg_test as
#      begin
#          procedure sp_test(
#              a_base_doc_id int,
#              a_base_doc_oper_id int -- (one of parameters to packaged procedure)
#          ) as
#          begin
#             -- nop --
#          end
#  
#          function fn_test(
#              a_base_doc_id int,
#              a_base_doc_oper_id int -- (one of parameters to packaged procedure)
#          ) returns int as
#          begin
#              return 1;
#          end
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  
#  f_init_sql = open( os.path.join(context['temp_directory'], 'tmp_6527_init.sql'), 'w' )
#  f_init_sql.write( sql_ddl )
#  flush_and_close( f_init_sql )
#  
#  
#  f_init_log = open( os.path.join(context['temp_directory'], 'tmp_6527_init.log'), 'w' )
#  f_init_err = open( os.path.join(context['temp_directory'], 'tmp_6527_init.err'), 'w' )
#  
#  subprocess.call( [ context['isql_path'], dsn, "-q", "-i", f_init_sql.name ],
#                   stdout = f_init_log,
#                   stderr = f_init_err
#                 )
#  
#  flush_and_close( f_init_log )
#  flush_and_close( f_init_err )
#  
#  f_meta_sql = open( os.path.join(context['temp_directory'],'tmp_meta_6527.sql'), 'w')
#  f_meta_err = open( os.path.join(context['temp_directory'],'tmp_meta_6527.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], "-x", dsn],
#                   stdout = f_meta_sql,
#                   stderr = f_meta_err
#                 )
#  
#  flush_and_close( f_meta_sql )
#  flush_and_close( f_meta_err )
#  
#  f_apply_log = open( os.path.join(context['temp_directory'],'tmp_apply_6527.log'), 'w')
#  f_apply_err = open( os.path.join(context['temp_directory'],'tmp_apply_6527.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], 'localhost:'+temp_fdb, "-i", f_meta_sql.name ],
#                   stdout = f_apply_log,
#                   stderr = f_apply_err
#                 )
#  
#  flush_and_close( f_apply_log )
#  flush_and_close( f_apply_err )
#  
#  # Check:
#  ########
#  
#  # Output must be empty:
#  with open( f_meta_err.name,'r') as f:
#      for line in f:
#          print("METADATA EXTRACTION PROBLEM, STDERR: "+line)
#  
#  # Output must be empty:
#  with open( f_apply_err.name,'r') as f:
#      for line in f:
#          print("METADATA APPLYING PROBLEM, STDERR: "+line)
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( (f_init_sql, f_init_log, f_init_err,f_meta_sql, f_meta_err, f_apply_log, f_apply_err, temp_fdb) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.8')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


