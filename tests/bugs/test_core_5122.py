#coding:utf-8
#
# id:           bugs.core_5122
# title:        Expression index may not be used by the optimizer if created and used in different connection charsets
# decription:   
#                  Confirmed:
#                     wrong plan (natural scan) on: WI-V3.0.0.32358.
#                     plan with index usage on:     WI-T4.0.0.32371, WI-V2.5.6.26979.
#                
# tracker_id:   CORE-5122
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
#  import fdb
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
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
#  con1 = fdb.connect(dsn=dsn, charset='iso8859_1')
#  
#  cur1=con1.cursor()
#  cur1.execute("recreate table test(s varchar(10))")
#  cur1.execute("create index test_calc_s on test computed by ( 'zxc' || s )")
#  con1.commit()
#  con1.close()
#  
#  sql_data_cmd=open( os.path.join(context['temp_directory'],'tmp_data_5122.sql'), 'w')
#  sql_data_cmd.write("set planonly; select * from test where 'zxc' || s starting with 'qwe';")
#  sql_data_cmd.close()
#  
#  sql_data_log=open( os.path.join(context['temp_directory'],'tmp_data_5122.log'), 'w')
#  
#  subprocess.call([context['isql_path'], dsn, "-n", "-ch", "utf8", "-i", sql_data_cmd.name], stdout = sql_data_log, stderr=subprocess.STDOUT)
#  flush_and_close( sql_data_log )
#  
#  with open(sql_data_log.name) as f:
#      print(f.read())
#  
#  # Cleanup.
#  ##########
#  time.sleep(1)
#  cleanup( (sql_data_log, sql_data_cmd) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST INDEX (TEST_CALC_S))
  """

@pytest.mark.version('>=2.5.6')
@pytest.mark.xfail
def test_core_5122_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


