#coding:utf-8
#
# id:           bugs.core_6089
# title:        BLOBs are unnecessarily copied during UPDATE after a table format change
# decription:   
#                   It's not easy to obtain BLOB_ID using only fdb. Rather in ISQL blob_id will be shown always (even if we do not want this :)).
#                   This test runs ISQL with commands that were provided in the ticket and parses its result by extracting only column BLOB_ID.
#                   Each BLOB_ID is added to set(), so eventually we can get total number of UNIQUE blob IDs that were generated during test.
#                   This number must be equal to number of records in the table (three in this test).
#               
#                   Confirmed bug on: 4.0.0.1535; 3.0.5.33142.
#                   Works fine on:
#                      4.0.0.1556: OK, 3.384s.
#                      3.0.5.33152: OK, 2.617s.
#               
#                
# tracker_id:   CORE-6089
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
#  import re
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
#  allowed_patterns = ( re.compile('COL2_BLOB_ID\\s+\\S+', re.IGNORECASE), )
#  
#  sql_txt='''
#      set bail on;
#      set list on;
#      set blob off;
#      recreate table t (col1 int, col2 blob);
#      recreate view v as select col2 as col2_blob_id from t; -- NB: alias for column have to be matched to re.compile() argument
#      commit;
#  
#      insert into t values (1, '1');
#      insert into t values (2, '2');
#      insert into t values (3, '3');
#      commit;
#  
#      select v.* from v;
#      update t set col1 = -col1;
#      select v.* from v;
#  
#  
#      rollback;
#      alter table t add col3 date;
#      select v.* from v;
#      update t set col1 = -col1;
#      select v.* from v; -- bug was here
#      quit;
#  '''
#  
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_6089.sql'), 'w')
#  f_isql_cmd.write( sql_txt )
#  flush_and_close( f_isql_cmd )
#  
#  f_isql_log=open( os.path.join(context['temp_directory'],'tmp_6089.log'), 'w')
#  
#  subprocess.call([context['isql_path'], dsn, "-q", "-i", f_isql_cmd.name], stdout=f_isql_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_isql_log )
#  
#  blob_id_set=set()
#  with open( f_isql_log.name,'r') as f:
#      for line in f:
#          match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#          if match2some:
#              blob_id_set.add( line.split()[1] )
#  
#  print( 'Number of unique blob IDs: ' + str(len(blob_id_set)) )
#  
#  # Cleanup.
#  ##########
#  cleanup( (f_isql_cmd, f_isql_log) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Number of unique blob IDs: 3
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


