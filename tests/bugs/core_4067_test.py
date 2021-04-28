#coding:utf-8
#
# id:           bugs.core_4067
# title:        Creating external function (udf) to not existing dll - and then procedure with it - crash server
# decription:   
#                
# tracker_id:   CORE-4067
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  tmpfdb_1=os.path.join(context['temp_directory'],'tmp_4067_1.fdb')
#  
#  sql_chk='''
#      set sql dialect 1;
#      create database 'localhost:%(tmpfdb_1)s' page_size 4096 default character set win1251 collation win1251;
#      set list on;
#      select mon$sql_dialect as x from mon$database;
#  ''' % locals()
#  
#  f_list=[tmpfdb_1]
#  
#  # Cleanup BEFORE running script:
#  ################
#  
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i]):
#          os.remove(f_list[i])
#  
#  runProgram('isql',['-q'], sql_chk)
#  
#  # Final cleanup:
#  ################
#  
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i]):
#          os.remove(f_list[i])
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


