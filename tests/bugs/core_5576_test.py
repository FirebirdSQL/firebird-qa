#coding:utf-8
#
# id:           bugs.core_5576
# title:        Bugcheck on queries containing WITH LOCK clause
# decription:    
#                  We create database as it was show in the ticket and do backup and restore of it.
#                  Then we run checking query - launch isql two times and check that 2nd call of ISQL
#                  does not raise bugcheck. Finally we run online validation against this DB.
#               
#                  Neither test query nor validation should raise any output in the STDERR.
#               
#                  Confirmed bug on 4.0.0.684 and 3.0.3.32743, got:
#                  ===
#                      Statement failed, SQLSTATE = XX000
#                      internal Firebird consistency check (decompression overran buffer (179), file: sqz.cpp line: 282)
#                      Statement failed, SQLSTATE = XX000
#                      internal Firebird consistency check (can't continue after bugcheck)
#                  ===
#                  Results after fix:
#                  fb30Cs, build 3.0.3.32746: OK, 6.328s.
#                  fb30SC, build 3.0.3.32746: OK, 3.469s.
#                  FB30SS, build 3.0.3.32746: OK, 3.172s.
#                  FB40CS, build 4.0.0.685: OK, 5.954s.
#                  FB40SC, build 4.0.0.685: OK, 3.781s.
#                  FB40SS, build 4.0.0.685: OK, 2.828s.
#                
# tracker_id:   CORE-5576
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = [('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]', ''), ('Relation [0-9]{3,4}', 'Relation')]

init_script_1 = """
      recreate table test (
          i integer not null primary key,
          d char(1024) computed by ('qwert'),
          s varchar(8192)
      );
      insert into test values (1, 'format1opqwertyuiopqwertyuiop');
      commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  
#  import os
#  import subprocess
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
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
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  f_bkrs_err = open( os.path.join(context['temp_directory'],'tmp_backup_restore_5576.err'), 'w')
#  f_bkup_tmp = os.path.join(context['temp_directory'],'tmp_5576.fbk')
#  f_rest_tmp = os.path.join(context['temp_directory'],'tmp_5576.fdb')
#  
#  cleanup( (f_bkup_tmp,f_rest_tmp) )
#  
#  fn_nul = open(os.devnull, 'w')
#  subprocess.call( [context['gbak_path'], "-b", dsn, f_bkup_tmp ],
#                   stdout = fn_nul,
#                   stderr = f_bkrs_err
#                 )
#  
#  subprocess.call( [context['gbak_path'], "-rep", f_bkup_tmp, 'localhost:'+f_rest_tmp ],
#                   stdout = fn_nul,
#                   stderr = f_bkrs_err
#                 )
#  
#  flush_and_close( f_bkrs_err )
#  fn_nul.close()
#  
#  
#  script='set list on;select 1 x1 from test where i=1 with lock;'
#  
#  # Checking query (it did produce bugcheck before fix):
#  ################
#  runProgram('isql',['localhost:'+f_rest_tmp],script)
#  runProgram('isql',['localhost:'+f_rest_tmp],script) # ---------- launch isql SECOND time!
#  
#  
#  f_val_log=open( os.path.join(context['temp_directory'],'tmp_val_5576.log'), "w")
#  f_val_err=open( os.path.join(context['temp_directory'],'tmp_val_5576.err'), "w")
#  
#  subprocess.call([context['fbsvcmgr_path'],"localhost:service_mgr",
#                   "action_validate",
#                   "dbname", f_rest_tmp
#                  ],
#                  stdout=f_val_log,
#                  stderr=f_val_err)
#  flush_and_close( f_val_log )
#  flush_and_close( f_val_err )
#  
#  with open( f_val_log.name,'r') as f:
#      print(f.read())
#  
#  # Check that neither restore nor validation raised errors:
#  ###################
#  f_list=(f_bkrs_err, f_val_err)
#  for i in range(len(f_list)):
#      with open( f_list[i].name,'r') as f:
#          for line in f:
#              if line.split():
#                  print( 'UNEXPECTED STDERR in file '+f_list[i].name+': '+line.upper() )
#  
#  
#  # Cleanup
#  #########
#  cleanup( (f_bkrs_err, f_val_log, f_val_err, f_bkup_tmp, f_rest_tmp) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X1                              1
    X1                              1
    Validation started
    Relation 128 (TEST)
      process pointer page    0 of    1
    Index 1 (RDB$PRIMARY1)
    Relation 128 (TEST) is ok
    Validation finished
  """

@pytest.mark.version('>=3.0.3')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


