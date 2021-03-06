#coding:utf-8
#
# id:           bugs.core_6090
# title:        BLOB fields may be suddenly set to NULLs during UPDATE after a table format change
# decription:   
#                   It's not easy to obtain BLOB_ID using only fdb. Rather in ISQL blob_id will be shown always (even if we do not want this :)).
#                   This test runs ISQL with commands that were provided in the ticket and parses its result by extracting only column BLOB_ID.
#                   Each BLOB_ID is added to set(), so eventually we can get total number of UNIQUE blob IDs that were generated during test.
#                   This number must be equal to number of records in the table (three in this test).
#                   Beside of this, we check that all blobs are not null, see 'null_blob_cnt' counter.
#               
#                   Confirmed bug on: 4.0.0.1535; 3.0.5.33142.
#                   Works fine on:
#                       4.0.0.1556: OK, 3.342s.
#                       3.0.5.33152: OK, 2.652s.
#                
# tracker_id:   CORE-6090
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
#  
#  db_conn.close()
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
#  allowed_patterns = ( re.compile('BLOB_ID\\s+\\S+', re.IGNORECASE), )
#  
#  sql_txt='''
#      set bail on;
#      set blob all;
#      set list on;
#  
#      recreate view v as select 1 x from rdb$database;
#      commit;
#      recreate table test (n1 int, n2 int, n3 int, blob_id blob);
#      recreate view v as select blob_id from test;
#      commit;
#  
#      insert into test values (0, 0, null, '0:foo');
#      insert into test values (1, 1, 1,    '1:rio');
#      insert into test values (2, 2, 2,    '2:bar');
#      commit;
#  
#      select 1 as point, v.* from v;
#  
#      update test set n1 = 1 where n2 >= 0; -- n1 should be set to 1 in all three rows
#      select 2 as point, v.* from v;
#      rollback;
#  
#      update test set n1 = 1 where n2 >= 0 and n3 >= 0; -- n1 should be set to 1 in 2nd and 3rd rows
#      select 3 as point, v.* from v;
#      rollback;
#  
#      alter table test add col5 date;
#      commit;
#  
#      update test set n1 = 1 where n2 >= 0; -- n1 should be set to 1 in all three rows
#      select 4 as point, v.* from v; -- Here blob_id were changed because of other bug, see CORE-6089, but contents is correct
#      rollback;
#  
#      update test set n1 = 1 where n2 >= 0 and n3 >= 0;
#      -- n1 should be set to 1 in 2nd and 3rd rows
#      select 5 as point, v.* from v; -- BUG: BLOB_ID in the second row was nullified!!! 
#  
#      quit;
#  '''
#  
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_6090.sql'), 'w')
#  f_isql_cmd.write( sql_txt )
#  flush_and_close( f_isql_cmd )
#  
#  f_isql_log=open( os.path.join(context['temp_directory'],'tmp_6090.log'), 'w')
#  
#  subprocess.call([context['isql_path'], dsn, "-q", "-i", f_isql_cmd.name], stdout=f_isql_log, stderr=subprocess.STDOUT)
#  flush_and_close( f_isql_log )
#  
#  blob_id_set=set()
#  null_blob_cnt=0
#  with open( f_isql_log.name,'r') as f:
#      for line in f:
#          match2some = filter( None, [ p.search(line) for p in allowed_patterns ] )
#          if match2some:
#              blob_id_set.add( line.split()[1] )
#              if '<null>' in line.lower():
#                  null_blob_cnt += 1
#  
#  print( 'Number of unique blob IDs: ' + str(len(blob_id_set)) )
#  print( 'Number of nullified blobs: ' + str(null_blob_cnt) )
#  
#  # Cleanup.
#  ##########
#  time.sleep(1)
#  cleanup( (f_isql_cmd, f_isql_log) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Number of unique blob IDs: 3
    Number of nullified blobs: 0
  """

@pytest.mark.version('>=3.0.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


