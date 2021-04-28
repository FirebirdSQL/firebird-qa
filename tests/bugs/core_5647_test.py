#coding:utf-8
#
# id:           bugs.core_5647
# title:        Increase number of formats/versions of views from 255 to 32K
# decription:    
#                  FB40SS, build 4.0.0.789: OK, 3.828s (SS, CS).
#                  Older version issued:
#                       Statement failed, SQLSTATE = 54000
#                       unsuccessful metadata update
#                       -TABLE VW1
#                       -too many versions
#                  NB: we have to change FW to OFF in order to increase speed of this test run thus use test_type = Python.
#                
# tracker_id:   CORE-5647
# min_versions: ['4.0']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  runProgram('gfix',[dsn,'-w','async'])
#  
#  script='''
#      set bail on;
#      set list on;
#      set term ^;
#      execute block returns(ret_code smallint) as
#          declare n int = 300;
#      begin
#          while (n > 0) do
#            begin
#              if (mod(n, 2) = 0) then
#                begin
#                  in autonomous transaction do
#                    begin
#                      execute statement 'create or alter view vw1 (dump1) as select 1 from rdb$database';
#                    end
#                end
#              else
#                begin
#                  in autonomous transaction do
#                    begin
#                      execute statement 'create or alter view vw1 (dump1, dump2) as select 1, 2 from rdb$database';
#                    end
#                end
#              n = n - 1;
#            end
#            ret_code = -abs(n);
#            suspend;
#      end ^
#      set term ;^
#      quit;
#  '''
#  runProgram('isql',[dsn],script)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RET_CODE                        0
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


