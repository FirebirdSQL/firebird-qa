#coding:utf-8
#
# id:           bugs.core_4882
# title:        ISQL input command (or -i option) reads large (> 64K) lines incorrectly
# decription:   
#                   This test verifies ability of parsing multiple statements that are going as `single-lined stream`.
#                   Source for this test is file `fbt-repo
#               iles\\core_4882.sql`.
#                   It contains almost all source code of test that emulates OLTP workload - without initial script for data filling.
#                   This test can be found here: svn://svn.code.sf.net/p/firebird/code/qa/oltp-emul/
#                   Three files were taken from it: oltp30_DDL.sql, oltp30_sp.sql and oltp_main_filling.sql - with total size  ~600 Kb.
#                   Then all single-lined comments ("-- blah blah ...") were removed and remained source code was pulled out in single-line.
#                   This single-line also could not be compiled up to WI-V3.0.0.31948, raising 'token unknown'.
#                   No error on compiling should occur since buiild WI-V3.0.0.31981.
#                   NOTE: before this file also contained lines with bulk of begin..end blocks but since CORE-4884 was fixed that number
#                   is limited to 512. With this limit single-line statement of begin-end blocks will have length less than 64K. For that
#                   reason these lines were removed from here to the test for CORE-4884.
#                 
# tracker_id:   CORE-4882
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('exception [0-9]+', 'exception'), ('After line [0-9]+ in file.*', ''), ('CURRENT_TIMESTAMP.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  
#  db_conn.close()
#  scriptfile=open(os.path.join(context['files_location'],'core_4882.sql'),'r')
#  scriptfile.close()
#  runProgram('isql',[dsn,'-user',user_name,'-pas',user_password,'-i',scriptfile.name])
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             oltp30_DDL.sql start
    MSG                             oltp30_DDL.sql finish
    MSG                             oltp30_sp.sql start
    MSG                             oltp30_sp.sql finish
    MSG                             oltp_main_filling.sql start
    MSG                             oltp_main_filling.sql finish
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


