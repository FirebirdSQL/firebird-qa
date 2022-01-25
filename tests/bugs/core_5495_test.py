#coding:utf-8

"""
ID:          issue-5764
ISSUE:       5764
TITLE:       New users or changed passwords in legacy authentication do not work in Firebird 4
DESCRIPTION:
  Used config:
   AuthServer = Legacy_Auth,Srp
   AuthClient = Legacy_Auth,Srp,Win_Sspi
   WireCrypt = Disabled
   UserManager = Srp, Legacy_UserManager
NOTES:
[3.11.2021] pcisar
  This test fails with 4.0, even with specified config
  Although user is created, the connect as user tmp$c5495 fails (unknown user)
JIRA:        CORE-5495
"""

import pytest
from firebird.qa import *

db = db_factory()

test_user = user_factory('db', name='tmp$c5495', password='123', plugin='Legacy_UserManager')

test_script = """
    set list on;
    set bail on;
    connect '$(DSN)' user tmp$c5495 password '123';
    --select mon$user,mon$remote_address,mon$remote_protocol,mon$client_version,mon$remote_version,mon$auth_method from mon$attachments
    select mon$user,mon$remote_protocol,mon$auth_method from mon$attachments
    where mon$attachment_id=current_connection;
    commit;
    connect '$(DSN)' user SYSDBA password 'masterkey';
    commit;
"""

act = isql_act('db', test_script, substitutions=[('TCPv.*', 'TCP')])

expected_stdout = """
     MON$USER                        TMP$C5495
     MON$REMOTE_PROTOCOL             TCP
     MON$AUTH_METHOD                 Legacy_Auth
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, test_user: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

