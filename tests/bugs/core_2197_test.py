#coding:utf-8
#
# id:           bugs.core_2197
# title:        Add support for -nodbtriggers switch in gbak into services API
# decription:   
#                  We add two database triggers (on connect and on disconnect) and make them do real work only when 
#                  new attachment will be established (see trick with rdb$get_context('USER_SESSION', 'INIT_STATE') ).
#                  After finish backup we restore database and check that there is no records in 'log' table.
#                  (if option 'bkp_no_triggers' will be omitted then two records will be in that table).
#                  Checked on:
#                      2.5.9.27103: OK, 0.938s.
#                      3.0.4.32920: OK, 2.875s.
#                      4.0.0.912: OK, 3.328s.
#                
# tracker_id:   CORE-2197
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table log( att bigint default current_connection, event_name varchar(20) );
    create sequence g;
    set term ^;
    create or alter trigger trg_attach inactive on connect as
    begin
        if ( rdb$get_context('USER_SESSION', 'INIT_STATE') is null ) then
            insert into log(event_name) values ('attach');
    end
    ^
    create or alter trigger trg_detach inactive  on disconnect as
    begin
        if ( rdb$get_context('USER_SESSION', 'INIT_STATE') is null ) then
            insert into log(event_name) values ('detach');
    end
    ^
    set term ^;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  thisdb='$(DATABASE_LOCATION)bugs.core_2197.fdb'
#  tmpbkp='$(DATABASE_LOCATION)bugs.core_2197_fbk.tmp'
#  tmpres='$(DATABASE_LOCATION)bugs.core_2197_new.tmp'
#  
#  
#  #---------------------------------------------------------------
#  
#  isql_txt='''    delete from log;
#      commit;
#      set term ^;
#      execute block as begin
#         rdb$set_context('USER_SESSION', 'INIT_STATE','1');
#      end
#      ^
#      set term ;^
#      alter trigger trg_attach active;
#      alter trigger trg_detach active;
#      commit;
#      --set count on;
#      --select * from log;
#  '''
#  
#  runProgram('isql',[dsn], isql_txt)
#  
#  f_svc_log=open( os.path.join(context['temp_directory'],'tmp_svc_2197.log'), 'w')
#  f_svc_err=open( os.path.join(context['temp_directory'],'tmp_svc_2197.err'), 'w')
#  
#  subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_backup', 
#                     'dbname', thisdb, 'bkp_file', tmpbkp,
#                     'bkp_no_triggers'
#                   ], 
#                   stdout=f_svc_log,stderr=f_svc_err
#                 )
#  
#  runProgram('isql',[dsn, '-nod'], 'set list on; set count on; select 1, g.* from log g;')
#  
#  subprocess.call( [ context['fbsvcmgr_path'], 'localhost:service_mgr','action_restore', 
#                     'bkp_file', tmpbkp, 'dbname', tmpres, 
#                     'res_replace'
#                   ], 
#                   stdout=f_svc_log,stderr=f_svc_err
#                 )
#  
#  f_svc_log.close()
#  f_svc_err.close()
#  
#  runProgram('isql',[dsn, '-nod'], 'set list on; set count on; select 1, g.* from log g;')
#  
#  
#  #############################################
#  # Cleanup.
#  f_list=( 
#      f_svc_log
#     ,f_svc_err
#  )
#  
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#  
#  os.remove(tmpbkp)
#  os.remove(tmpres)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
    Records affected: 0
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


