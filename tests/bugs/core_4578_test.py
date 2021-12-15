#coding:utf-8
#
# id:           bugs.core_4578
# title:        INPUT file not properly closed
# decription:
#                  Confirmed bug in ISQL 3.0.0.31374 (Beta1 release): script that has been performed by "IN" command
#                  is NOT deleted by "shell del ..." and can be used again, so the output will be:
#                  ID                              1
#                  <path>	mp_4578_in.sql
#                  ID                              1
#
#
# tracker_id:   CORE-4578
# min_versions: ['2.5.4']
# versions:     2.5.4
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5.4
# resources: None

substitutions_1 = [('Unable to open.*', 'Unable to open')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import subprocess
#  import time
#
#  db_conn.close()
#
#  txt_in = '''set list on;
#  recreate table test(id int);
#  commit;
#  insert into test values(1);
#  select id from test;
#  commit;
#  '''
#  tmp_input_sql=open( os.path.join(context['temp_directory'],'tmp_4578_in.sql'), 'w')
#  tmp_input_sql.write(txt_in)
#  tmp_input_sql.close()
#
#  sql_main_file=open( os.path.join(context['temp_directory'],'tmp_4578_go.sql'), 'w')
#
#  sql_main_file.write("set bail on;\\n" )
#  sql_main_file.write("in "+tmp_input_sql.name+";\\n" )
#  sql_main_file.write("shell del "+tmp_input_sql.name+" 2>nul;\\n" )
#  sql_main_file.write("in "+tmp_input_sql.name+";\\n" )
#
#  sql_main_file.close()
#
#  sql_main_log=open( os.path.join(context['temp_directory'],'tmp_isql_4578.log'), 'w')
#  p_isql = subprocess.call([ "isql" , dsn, "-user" , "SYSDBA" , "-password", "masterkey", "-i", sql_main_file.name ], stdout=sql_main_log, stderr=subprocess.STDOUT)
#  sql_main_log.close()
#
#  time.sleep(1)
#
#  with open( sql_main_log.name,'r') as f:
#        print(f.read())
#  f.close()
#
#  # do NOT remove this pause otherwise log of trace will not be enable for deletion and test will finish with
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#
#  os.remove(sql_main_log.name)
#  os.remove(sql_main_file.name)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    Unable to open
  """

@pytest.mark.version('>=2.5.4')
@pytest.mark.platform('Windows')
@pytest.mark.xfail
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


