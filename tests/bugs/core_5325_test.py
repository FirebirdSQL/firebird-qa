#coding:utf-8
#
# id:           bugs.core_5325
# title:        Malformed string error when using cyrilic symbols and x'0d0a' in exception
# decription:   
#                   Ticked is marked as Won't fix, but it seems that sample shown by Adriano is useful for testing.
#                   Checked on old versions: 3.0.0.32483, 3.0.2.32703, 3.0.4.32972 -- works OK.
#               
#                   05-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#                   Test encodes to UTF8 all needed statements (SET NAMES; CONNECT; DDL and DML) and stores this text in .sql file.
#                   NOTE: 'SET NAMES' contain character set that must be used for reproducing problem (WIN1251 in this test).
#                   Then ISQL is launched in separate (child) process which performs all necessary actions (using required charset).
#                   Result will be redirected to log(s) which will be opened further via codecs.open(...encoding='cp1251').
#                   Finally, its content will be converted to UTF8 for showing in expected_stdout.
#                   Checked on:
#                   * Windows: 4.0.0.2377
#                   * Linux:   4.0.0.2379, 3.0.8.33415
#                
# tracker_id:   CORE-5325
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('exception [\\d]+', 'exception'), ('-At block line(:)?\\s+[\\d]+.*', ''), ('After line(:)?\\s+[\\d]+.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import codecs
#  import subprocess
#  import time
#  engine = db_conn.engine_version
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
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  sql_txt='''    set bail on;
#      set names win1251;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#      
#      create exception error_test 'йцукенг';
#      commit;
#      set term ^;
#      execute block as
#      begin
#          exception error_test 'йцу' || _win1251 x'0d0a' || 'кенг';
#      end^
#      set term ;^  
#  
#  ''' % dict(globals(), **locals())
#  
#  f_run_sql = open( os.path.join(context['temp_directory'], 'tmp_5325_win1251.sql'), 'w' )
#  f_run_sql.write( sql_txt.decode('utf8').encode('cp1251') )
#  flush_and_close( f_run_sql )
#  
#  # result: file tmp_5325_win1251.sql is encoded in win1251
#  
#  f_run_log = open( os.path.splitext(f_run_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_run_sql.name ],
#                   stdout = f_run_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_run_log ) # result: output will be encoded in win1251
#  
#  with codecs.open(f_run_log.name, 'r', encoding='cp1251' ) as f:
#      result_in_win1251 = f.readlines()
#  
#  for i in result_in_win1251:
#      print( i.encode('utf8') )
#  
#  # cleanup:
#  ###########
#  cleanup( (f_run_sql, f_run_log) )
#    
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -ERROR_TEST
    -йцу

    кенг
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


