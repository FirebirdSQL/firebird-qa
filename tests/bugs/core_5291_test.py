#coding:utf-8
#
# id:           bugs.core_5291
# title:        Error messages differ when regular user tries to RESTORE database, depending on his default role and (perhaps) system privilege USE_GBAK_UTILITY
# decription:   
#                  Works fine on 4.0.0.316.
#                
# tracker_id:   CORE-5291
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('gbak: ERROR:no permission for CREATE access to DATABASE.*', 'gbak: ERROR:no permission for CREATE access to DATABASE'), ('gbak: ERROR:    failed to create database.*', 'gbak: ERROR:    failed to create database'), ('gbak: ERROR:failed to create database localhost:.*', 'gbak: ERROR:failed to create database localhost')]

init_script_1 = """
    set wng off;
    create or alter user tmp$c5291_1 password '123' revoke admin role;
    create or alter user tmp$c5291_2 password '456' revoke admin role;
    commit;
    revoke all on all from tmp$c5291_1;
    revoke all on all from tmp$c5291_2;
    commit;
    create role role_for_use_gbak_utility set system privileges to USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE;
    commit;
    grant default role_for_use_gbak_utility to user tmp$c5291_2;
    commit; 
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  tmpfbk=os.path.join(context['temp_directory'],'tmp_core_5291.fbk')
#  tmpres1=os.path.join(context['temp_directory'],'tmp_core_5291_1.tmp')
#  tmpres2=os.path.join(context['temp_directory'],'tmp_core_5291_2.tmp')
#  
#  runProgram('gbak',['-b', dsn, tmpfbk])
#  
#  runProgram('gbak',['-se', 'localhost:service_mgr', '-rep', tmpfbk, tmpres1, '-user', 'tmp$c5291_1', '-pas', '123'])
#  runProgram('gbak',['-rep', tmpfbk, 'localhost:' + tmpres2, '-user', 'tmp$c5291_1', '-pas', '123'])
#  
#  runProgram('gbak',['-se', 'localhost:service_mgr', '-rep', tmpfbk, tmpres1, '-user', 'tmp$c5291_2', '-pas', '456'])
#  runProgram('gbak',['-rep', tmpfbk, 'localhost:' + tmpres2, '-user', 'tmp$c5291_2', '-pas', '456'])
#  
#  runProgram('isql',[dsn],'drop user tmp$c5291_1; drop user tmp$c5291_2;')
#  
#  f_list=[tmpfbk, tmpres1, tmpres2]
#  
#  for i in range(len(f_list)):
#     if os.path.isfile(f_list[i]):
#         os.remove(f_list[i])
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:    failed to create database
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database localhost
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:    failed to create database
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database localhost
    gbak:Exiting before completion due to errors
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


