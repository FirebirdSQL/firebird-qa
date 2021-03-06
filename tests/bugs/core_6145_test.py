#coding:utf-8
#
# id:           bugs.core_6145
# title:        Wrong result in "similar to" with non latin characters
# decription:   
#               	Confirmed bug on 4.0.0.1607
#               	Checked on:
#               		4.0.0.1614: OK, 1.509s.
#               		3.0.5.33171: OK, 0.682s.
#               		2.5.9.27142: OK, 0.629s.	
#               
#                   15.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 4.0.0.2416
#                     Linux:   4.0.0.2416
#                
# tracker_id:   CORE-6145
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
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
#  non_ascii_ddl='''
#      set bail on;
#      set list on;
#      set names win1251;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#      set count on;
#  	set heading off;
#  	-- NB: When this script is Python variable then we have to use DUPLICATE percent signs!
#  	-- Otherwise get: "not enough arguments for format string"
#  	select 1 result_1 from rdb$database where 'я' similar to '%%Я%%'; 
#  	select 2 result_2 from rdb$database where 'Я' similar to '%%я%%'; 
#  	select 3 result_3 from rdb$database where 'я' similar to '[Яя]'; 
#      select 4 result_4 from rdb$database where 'Я' similar to 'я';
#      select 5 result_5 from rdb$database where 'Я' similar to 'Я';
#      select 6 result_6 from rdb$database where 'Я' similar to '[яЯ]';
#  ''' % dict(globals(), **locals())
#  
#  f_ddl_sql = open( os.path.join(context['temp_directory'], 'tmp_6145_w1251.sql'), 'w' )
#  f_ddl_sql.write( non_ascii_ddl.decode('utf8').encode('cp1251') )
#  flush_and_close( f_ddl_sql )
#  
#  f_run_log = open( os.path.join(context['temp_directory'],'tmp_6145.log'), 'w')
#  f_run_err = open( os.path.join(context['temp_directory'],'tmp_6145.err'), 'w')
#  
#  subprocess.call( [context['isql_path'], "-q", "-i", f_ddl_sql.name ],
#                   stdout = f_run_log,
#                   stderr = f_run_err
#                 )
#  
#  flush_and_close( f_run_log )
#  flush_and_close( f_run_err )
#  
#  with open( f_run_log.name, 'r') as f:
#      for line in f:
#          if line.strip():
#              print( line.strip().decode("cp1251").encode('utf8') )
#  
#  with open( f_run_err.name, 'r') as f:
#      for line in f:
#          out_txt='UNEXPECTED STDERR: ';
#          if line.strip():
#              print( out_txt + line.strip().decode("cp1251").encode('utf8') )
#  
#  # cleanup:
#  ##########
#  time.sleep(1)
#  #cleanup( (f_ddl_sql, f_run_log, f_run_err) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
    Records affected: 0
    RESULT_3                        3
    Records affected: 1
    Records affected: 0
    RESULT_5                        5
    Records affected: 1
    RESULT_6                        6
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


