#coding:utf-8
#
# id:           bugs.core_6438
# title:        ISQL: bad headers when text columns has >= 80 characters
# decription:   
#                   Test creates .sql script with query that contains literal (similar to descriped in the ticket, but much longer).
#                   Then we parse result of this query and compare length of header and data. They both must be equal to the same value.
#                   Confirmed truncated length of header on 4.0.0.2225
#                   Checked on 4.0.0.2249 - all fine.
#                
# tracker_id:   CORE-6438
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import sys
#  import os
#  import time
#  import subprocess
#  from fdb import services
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
#      for f in f_names_list:
#         if type(f) == file:
#            del_name = f.name
#         elif type(f) == str:
#            del_name = f
#         else:
#            print('Unrecognized type of element:', f, ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#      
#  #--------------------------------------------
#  
#  data = '1' * 65533
#  sql_run = '''select '%(data)s' as " ", 1 as "  " from rdb$database;''' % locals()
#  
#  f_run_sql = open( os.path.join(context['temp_directory'],'tmp_6438.sql'), 'w')
#  f_run_sql.write(sql_run)
#  flush_and_close(f_run_sql)
#  
#  f_run_log=open( os.path.join(context['temp_directory'],'tmp_6438.log'), 'w')
#  subprocess.call( [ context['isql_path'], dsn, "-i", f_run_sql.name ], stdout=f_run_log, stderr=subprocess.STDOUT )
#  flush_and_close(f_run_log)
#  
#  hdr_len, txt_len = 0,0
#  with open(f_run_log.name,'r') as f:
#      for line in f:
#          if line.startswith('='):
#              hdr_len = len(line.split()[0])
#          elif line.startswith('1'):
#              txt_len = len(line.split()[0])
#  
#  print('hdr_len:', hdr_len)
#  print('txt_len:', txt_len)
#  
#  # Cleanup
#  ##########
#  cleanup( ( f_run_sql, f_run_log ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
hdr_len: 65533
txt_len: 65533
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


