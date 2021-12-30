#coding:utf-8
#
# id:           bugs.core_5039
# title:        Connecting to service with invalid servicename yields incorrect error message
# decription:
#                   28.01.2019.
#                   Name of service manager is ignored in FB 4.0, see http://tracker.firebirdsql.org/browse/CORE-5883
#                   ("service_mgr" to be cleaned out from connection string completely...")
#                   26.05.2021: changed code for FB 4.x and enabled after discuss with Alex.
#
# tracker_id:   CORE-5039
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  db_conn.close()
#  runProgram('fbsvcmgr',['localhost:qwe_mnb_zxc_9','user', user_name, 'password', user_password, 'info_server_version'])
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stderr_1 = """
    Cannot attach to services manager
    -service qwe_mnb_zxc_9 is not defined
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.svcmgr(switches=['localhost:qwe_mnb_zxc_9', 'user', 'SYSDBA',
                           'password', 'masterkey', 'info_server_version'],
                 connect_mngr=False)
    assert act_1.clean_stderr == act_1.clean_expected_stderr

# version: 4.0
# resources: None

substitutions_2 = [('Server version: .* Firebird \\d+\\.\\d+.*', 'Server version: Firebird')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
#
#  db_conn.close()
#  # Server version must be issued here, regardless on the (invalid/non-existing) name of service manager, e.g.:
#  # Server version: WI-V4.0.0.2491 Firebird 4.0 Release Candidate 1
#  runProgram('fbsvcmgr',['localhost:qwe_mnb_zxc_9','user', user_name, 'password', user_password, 'info_server_version'])
#---
act_2 = python_act('db_2', substitutions=substitutions_2)

expected_stdout_2 = """
    Server version: Firebird
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.svcmgr(switches=['localhost:qwe_mnb_zxc_9', 'user', 'SYSDBA',
                           'password', 'masterkey', 'info_server_version'],
                 connect_mngr=False)
    assert act_2.clean_stdout == act_2.clean_expected_stdout
