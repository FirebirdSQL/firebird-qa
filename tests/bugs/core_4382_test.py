#coding:utf-8
#
# id:           bugs.core_4382
# title:        User savepoints are not released on commit
# decription:   
#                   Added separate code for 4.0: one need to be sure that all changes have been flushed on disk before we launch gstat.
#                   See letter from hvlad, 02.02.2019 22:30.
#                   ::: NOTE :::
#                   !! It looks strange but if we put preparing statement in 'init_script' section than result of 'gstat -i' will be WRONG,
#                   even if we do db_conn.close() before runProgram('gstat' ...) !!
#                   Checked on:
#                       4.0.0.1421: OK, 3.340s. // SS, SC, CS
#                       3.0.5.33097: OK, 1.113s.
#                       2.5.9.27127: OK, 0.650s.
#                
# tracker_id:   CORE-4382
# min_versions: ['2.5.4']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!nodes).)*$', ''), ('Root page: [0-9]+,', ''), ('Depth', 'depth')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  
#  sql_prep='''
#      create table g_test (f integer);
#      create index g_ind on g_test (f);
#      insert into g_test values (1);
#      commit;
#      update g_test set f=2;
#      savepoint a;
#      update g_test set f=3;
#      savepoint b;
#      update g_test set f=4;
#      savepoint c;
#      update g_test set f=5;
#      savepoint d;
#      update g_test set f=6;
#      savepoint e;
#      update g_test set f=7;
#      commit;
#      select * from g_test; 
#  '''
#  runProgram( 'isql',[ '-q', dsn], sql_prep ),
#  runProgram( 'gstat',['-i', dsn] )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Root page: 203, depth: 1, leaf buckets: 1, nodes: 1
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


