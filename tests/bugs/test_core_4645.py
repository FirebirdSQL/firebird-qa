#coding:utf-8
#
# id:           bugs.core_4645
# title:        internal Firebird consistency check (cannot find tip page (165), file: tra.cpp line: 2375)
# decription:   
#                  Both STDOUT and STDERR in this test should be empty.
#                  Confirmed:
#                  1) bugcheck exception on 3.0.0.32378;  4.0.0.98:
#                      Statement failed, SQLSTATE = XX000
#                      internal Firebird consistency check (cannot find tip page (165), file: tra.cpp line: 2303)
#                      Statement failed, SQLSTATE = XX000
#                      internal Firebird consistency check (can't continue after bugcheck)
#                  2) normal work on 3.0.0.32471; 4.0.0.127.
#                
# tracker_id:   CORE-4645
# min_versions: ['2.5']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  db_conn.close()
#  runProgram('gfix',[dsn,'-user',user_name,'-pas',user_password,'-mode','read_only'])
#  script='''
#      commit;
#      set transaction read committed;
#      set term ^;
#      execute block as
#          declare n int = 20000;
#      begin
#          while (n>0) do 
#              in autonomous transaction do
#              select :n-1 from rdb$database into n;
#      end
#      ^
#      set term ;^
#      commit;
#  '''
#  runProgram('isql',[dsn,'-user',user_name,'-password',user_password],script)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.6')
@pytest.mark.xfail
def test_core_4645_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


