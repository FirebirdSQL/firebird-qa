#coding:utf-8

"""
ID:          issue-4894
ISSUE:       4894
TITLE:       INPUT file not properly closed
DESCRIPTION:
JIRA:        CORE-4578
FBTEST:      bugs.core_4578
"""

import pytest
from firebird.qa import *
db = db_factory()

act = python_act('db', substitutions=[('Unable to open.*', 'Unable to open')])

expected_stdout = """
    ID                              1
    Unable to open
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3')
@pytest.mark.platform('Windows')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

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
