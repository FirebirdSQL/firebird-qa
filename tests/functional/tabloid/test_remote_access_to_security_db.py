#coding:utf-8

"""
ID:          tabloid.remote-access-to-security-db
TITLE:       Verify ability to make REMOTE connect to security.db
DESCRIPTION: 
  This test verifies only ability to make REMOTE connect to security.db 
     Line "RemoteAccess = false" in file $FB_HOME/databases.conf should be COMMENTED.
     On the host that run tests this must is done BEFORE launch all testsby calling 
     batch file "upd_databases_conf.bat" (see \FirebirdQA\qa3x.bat; qa4x.bat).
     Checked 28.06.2016 on 4.0.0.267
FBTEST:      functional.tabloid.remote_access_to_security_db
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('TCPv4', 'TCP'), ('TCPv6', 'TCP')])

expected_stdout = """
    MON$ATTACHMENT_NAME             security.db
    MON$REMOTE_PROTOCOL             TCP
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3.0')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

# Original python code for this test:
# -----------------------------------
# 
# import os
# os.environ["ISC_USER"] = user_name
# os.environ["ISC_PASSWORD"] = user_password
# 
# db_conn.close()
# sql_chk='''
# connect 'localhost:security.db';
# set list on;
# select mon$attachment_name,mon$remote_protocol from mon$attachments where mon$attachment_id = current_connection;
# '''
# runProgram('isql',['-q'],sql_chk)
# -----------------------------------
