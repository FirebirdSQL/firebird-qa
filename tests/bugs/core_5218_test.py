#coding:utf-8
#
# id:           bugs.core_5218
# title:        Explicitly defined names for NOT NULL constraints are not exported into script by ISQL -x
# decription:   
#                  Checked on WI-V3.0.0.32501, WI-T4.0.0.155.
#                
# tracker_id:   CORE-5218
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(
       f01 int constraint f01_nn not null constraint f01_pk primary key
      ,f02 int constraint f02_nn not null constraint f02_uk unique
      -- NB: 3.0 allows to skip reference of PK column from table that
      --- is created now, i.e. one may to declare FK-field like this:
      -- ... f03 references test
      -- That's not so for 2.5.x:
      ,f03 int constraint f03_nn not null 
       constraint f03_fk 
       references test( f01 )
       --                ^-- this must be specified in 2.5.x
    );
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
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
#  f_extract_meta_sql = open( os.path.join(context['temp_directory'],'tmp_5218_meta.log'), 'w')
#  f_extract_meta_err = open( os.path.join(context['temp_directory'],'tmp_5218_meta.err'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-x"],
#                   stdout = f_extract_meta_sql,
#                   stderr = f_extract_meta_err
#                 )
#  flush_and_close( f_extract_meta_sql )
#  flush_and_close( f_extract_meta_err )
#  
#  ###############
#  # CHECK RESULTS
#  ###############
#  
#  # 1. STDERR for extracted metadata must be EMPTY.
#  with open( f_extract_meta_err.name, 'r') as f:
#      for line in f:
#          if line.strip():
#              print('EXTRACTED METADATA ERR: '+line)
#  
#  # 2. STDLOG for extracted metadata: we must ouput all
#  # lines with phrase 'CONSTRAINT' in order to check that this 
#  # keyword actually present for each initial declaration:
#  
#  with open( f_extract_meta_sql.name, 'r') as f:
#      for line in f:
#          if 'CONSTRAINT' in line:
#              print( 'EXTRACTED METADATA LOG: '+line )
#  
#  
#  # Cleanup:
#  ##########
#  time.sleep(1)
#  cleanup( (f_extract_meta_sql, f_extract_meta_err) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXTRACTED METADATA LOG: CREATE TABLE TEST (F01 INTEGER CONSTRAINT F01_NN NOT NULL,
    EXTRACTED METADATA LOG:         F02 INTEGER CONSTRAINT F02_NN NOT NULL,
    EXTRACTED METADATA LOG:         F03 INTEGER CONSTRAINT F03_NN NOT NULL,
    EXTRACTED METADATA LOG: CONSTRAINT F01_PK PRIMARY KEY (F01),
    EXTRACTED METADATA LOG: CONSTRAINT F02_UK UNIQUE (F02));
    EXTRACTED METADATA LOG: ALTER TABLE TEST ADD CONSTRAINT F03_FK FOREIGN KEY (F03) REFERENCES TEST (F01);
  """

@pytest.mark.version('>=2.5.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


