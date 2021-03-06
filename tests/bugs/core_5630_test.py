#coding:utf-8
#
# id:           bugs.core_5630
# title:        Shadow file is can not be created during restore when -use_all_space option is used
# decription:   
#                   Confirmed bug on WI-V3.0.3.32805, WI-T4.0.0.789.
#                   Restore process failed with messages:
#                   ===
#                       gbak: ERROR:I/O error during "ReadFile" operation for file <fdb-file-name>
#                       gbak: ERROR:    Error while trying to read from file
#                       gbak: ERROR:    <end-of-file encountered> // localized message
#                       gbak:Exiting before completion due to errors
#                   ===
#                   Works OK on:
#                       fb30Cs, build 3.0.3.32832: OK, 14.766s.
#                       FB30SS, build 3.0.3.32832: OK, 5.875s.
#                       FB40CS, build 4.0.0.796: OK, 7.344s.
#                       FB40SS, build 4.0.0.796: OK, 4.531s.
#                
# tracker_id:   CORE-5630
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
# import os
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  #-------------------------------------------
#  def del_tmp_files(f_list):
#      import os
#      for i in range(len(f_list)):
#          if os.path.isfile(f_list[i]):
#              os.remove(f_list[i])
#  #-------------------------------------------
#  
#  n_prefix="$(DATABASE_LOCATION)bugs.tmp.core.5630"
#  fdb_file=n_prefix + ".fdb"
#  shd_file=n_prefix + ".shd"
#  fbk_file=n_prefix + ".fbk"
#  
#  del_tmp_files( (fdb_file, shd_file, fbk_file) )
#  
#  usr=user_name
#  pwd=user_password
#  
#  sql_text='''
#      set bail on;
#      set list on;
#      
#      create database 'localhost:%(fdb_file)s' user '%(usr)s' password '%(pwd)s';
#  
#      recreate table test(s varchar(30));
#      commit;
#  
#      create or alter view v_shadow_info as
#      select 
#           rdb$file_sequence  --           0
#          ,rdb$file_start     --           0
#          ,rdb$file_length    --           0
#          ,rdb$file_flags     --           1
#          ,rdb$shadow_number  --           1
#      from rdb$files
#      where lower(rdb$file_name) containing lower('bugs.tmp.core.5630.shd')
#      ;
#  
#      insert into test select 'line #' || lpad(row_number()over(), 3, '0' ) from rdb$types rows 200;
#      commit;
#  
#      create shadow 1 '%(shd_file)s';
#      commit;
#      set list on;
#      select * from v_shadow_info;
#      select hash( list(s) ) as s_hash_before from test;
#      quit;
#  '''
#  
#  f_init_ddl = open( os.path.join(context['temp_directory'],'tmp_5630_ddl.sql'), 'w')
#  f_init_ddl.write( sql_text % locals() )
#  f_init_ddl.close()
#  
#  runProgram( 'isql',[ '-q', '-i', f_init_ddl.name ] )
#  runProgram( 'gbak',['-b', 'localhost:%s' % fdb_file, fbk_file ] )
#  
#  del_tmp_files( (fdb_file, shd_file) )
#  
#  # --------------------------------------
#  # restore using "-use_all_space" switch:
#  # --------------------------------------
#  runProgram( 'gbak',['-c', '-use_all_space', fbk_file, 'localhost:%s' % fdb_file ] )
#  
#  # Check that we have the same data in DB tables:
#  sql_text='''
#      set list on;
#      select * from v_shadow_info;
#      select hash( list(s) ) as s_hash_after from test;
#  '''
#  runProgram( 'isql',[ '-q', 'localhost:%s' % fdb_file ], sql_text )
#  
#  
#  ###############################
#  # Cleanup.
#  del_tmp_files( (fdb_file, shd_file, fbk_file, f_init_ddl.name) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FILE_SEQUENCE               0
    RDB$FILE_START                  0
    RDB$FILE_LENGTH                 0
    RDB$FILE_FLAGS                  1
    RDB$SHADOW_NUMBER               1
    S_HASH_BEFORE                   1499836372373901520

    RDB$FILE_SEQUENCE               0
    RDB$FILE_START                  0
    RDB$FILE_LENGTH                 0
    RDB$FILE_FLAGS                  1
    RDB$SHADOW_NUMBER               1
    S_HASH_AFTER                    1499836372373901520
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


