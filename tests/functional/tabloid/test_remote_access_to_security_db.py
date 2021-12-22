#coding:utf-8
#
# id:           functional.tabloid.remote_access_to_security_db
# title:        Verify ability to make REMOTE connect to security.db 
# decription:   
#                  This test verifies only ability to make REMOTE connect to security.db 
#                  Line "RemoteAccess = false" in file $FB_HOME/databases.conf should be COMMENTED.
#                  On the host that run tests this must is done BEFORE launch all testsby calling 
#                  batch file "upd_databases_conf.bat" (see \\FirebirdQA\\qa3x.bat; qa4x.bat).
#                  Checked 28.06.2016 on 4.0.0.267
#                
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('TCPv4', 'TCP'), ('TCPv6', 'TCP')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  sql_chk='''
#  connect 'localhost:security.db';
#  set list on;
#  select mon$attachment_name,mon$remote_protocol from mon$attachments where mon$attachment_id = current_connection;
#  '''
#  runProgram('isql',['-q'],sql_chk)
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    MON$ATTACHMENT_NAME             security.db
    MON$REMOTE_PROTOCOL             TCP
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    pytest.fail("Test not IMPLEMENTED")


