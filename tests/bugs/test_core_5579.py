#coding:utf-8
#
# id:           bugs.core_5579
# title:        request synchronization error in the GBAK utility (restore)
# decription:   
#                  Database for this test was created beforehand on 2.5.7 with intentionally broken not null constraint.
#                  It was done using direct RDB$ table modification:
#                  ---
#                     recreate table test(id int not null,fn int);
#                     insert into test(id, fn) values(1, null);
#                     insert into test(id, fn) values(2, null); -- 2nd record must also present!
#                     commit;
#                     -- add NOT NULL, direct modify rdb$ tables (it is allowed before 3.0):
#                     update rdb$relation_fields set rdb$null_flag = 1
#                     where rdb$field_name = upper('fn') and rdb$relation_name = upper('test');
#                     commit;
#                  ---
#                  We try to restore .fbk which was created from that DB on current FB snapshot and check that restore log 
#                  does NOT contain phrase 'request synchronization' in any line.
#               
#                  Bug was reproduced on 2.5.7.27062, 3.0.3.32746, 4.0.0.684
#                  All fine on:
#                       FB25Cs, build 2.5.8.27067: OK, 2.125s.
#                       FB25SC, build 2.5.8.27067: OK, 1.641s.
#                       fb30Cs, build 3.0.3.32756: OK, 3.891s.
#                       fb30SC, build 3.0.3.32756: OK, 2.500s.
#                       FB30SS, build 3.0.3.32756: OK, 2.422s.
#                       FB40CS, build 4.0.0.690: OK, 3.891s.
#                       FB40SC, build 4.0.0.690: OK, 2.750s.
#                       FB40SS, build 4.0.0.690: OK, 2.828s.
#                
# tracker_id:   CORE-5579
# min_versions: ['2.5.8']
# versions:     2.5.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import time
#  import zipfile
#  import subprocess
#  import re
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_5579_broken_nn.zip') )
#  
#  # Name of .fbk inside .zip:
#  zipfbk='core_5579_broken_nn.fbk'
#  
#  zf.extract( zipfbk, context['temp_directory'] )
#  zf.close()
#  
#  tmpfbk=''.join( ( context['temp_directory'], zipfbk ) )
#  tmpfdb=''.join( ( context['temp_directory'], 'core_5579_broken_nn.fdb') )
#  
#  # C:\\MIX
#  irebird\\QA
#  bt-repo	mp\\core_5579_broken_nn.fbk
#  # C:\\MIX
#  irebird\\QA
#  bt-repo	mp\\core_5579_broken_nn.fdb
#  
#  f_restore_log=open( os.path.join(context['temp_directory'],'tmp_restore_5579.log'), 'w')
#  f_restore_err=open( os.path.join(context['temp_directory'],'tmp_restore_5579.err'), 'w')
#  
#  if os.path.isfile(tmpfdb):
#      os.remove(tmpfdb)
#  
#  # C:\\MIX
#  irebird
#  b25Csin\\gbak -rep C:\\MIX
#  irebird\\QA
#  bt-repo	mp\\c5579.fbk\\core_5579_broken_nn.fbk -v -o /:C:\\MIX
#  irebird\\QA
#  bt-repo	mp\\c5579.fbk\\CORE_5579_BROKEN_NN.FDB
#  
#  subprocess.call([ "fbsvcmgr",
#                    "localhost:service_mgr",
#                    "action_restore",
#                    "bkp_file", tmpfbk,
#                    "dbname",   tmpfdb,
#                    "res_one_at_a_time"
#                  ],
#                  stdout=f_restore_log,
#                  stderr=f_restore_err
#                )
#  # before this ticket was fixed restore log did contain following line:
#  # gbak: ERROR:request synchronization error
#  
#  f_restore_log.close()
#  f_restore_err.close()
#  
#  # Check:
#  ########
#  # 1. fbsvcmgr itself must finish without errors:
#  with open( f_restore_err.name,'r') as f:
#      for line in f:
#          if line.split():
#              print( 'UNEXPECTED STDERR in file '+f_restore_err.name+': '+line.upper() )
#  
#  # 2. Log of restoring process must NOT contain line with phrase 'request synchronization':
#  
#  req_sync_pattern=re.compile('[.*]*request\\s+synchronization\\s+error\\.*', re.IGNORECASE)
#  
#  with open( f_restore_log.name,'r') as f:
#      for line in f:
#          if req_sync_pattern.search(line):
#              print( 'UNEXPECTED STDLOG: '+line.upper() )
#  
#  #####################################################################
#  # Cleanup:
#  
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  
#  f_list=(f_restore_log, f_restore_err)
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#  os.remove(tmpfdb)
#  os.remove(tmpfbk)
#  
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.8')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_core_5579_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


