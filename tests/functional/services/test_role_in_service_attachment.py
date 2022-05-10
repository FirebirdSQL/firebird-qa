#coding:utf-8

"""
ID:          services.role-in-service-attachment
TITLE:       Check that trace plugin shows ROLE used in service attachment. Format: USER[:ROLE]
DESCRIPTION:
  See: https://github.com/FirebirdSQL/firebird/commit/dd241208f203e54a9c5e9b8b24c0ef24a4298713
FBTEST:      functional.services.role_in_service_attachment

NOTES [pzotov]
    10.05.2022.
    It is unclear how to make FIRST connection to Services API as NON-SYSDBA account:
    method act.trace() has no parameters to specify user/password/role.
    Because of this, we check regexp only for lines that meet requirement:
    "if 'service_mgr' in line and tmp_user.name in line:" (rather than "if 'service_mgr' in line:")

    Checked on 4.0.1.2692, 5.0.0.489
"""

import re
import pytest
from firebird.qa import *
import firebird.driver
from firebird.driver import SrvStatFlag

tmp_user = user_factory('db', name='tmp_tracing_user', password='123')
db = db_factory()
tmp_role = role_factory('db', name='tmp_tracing_role')

act = python_act('db')

expected_stdout = """
    EXPECTED output found in the trace log
"""
@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_user: User, tmp_role:Role, capsys):

    init_script = \
    f'''
        set wng off;
        set bail on;
        revoke all on all from {tmp_user.name};
        commit;
        commit;
        -- Trace other users' attachments
        grant default {tmp_role.name} to user {tmp_user.name};
        commit;
    '''
    act.isql(switches=['-q'], input=init_script)

    trace_svc_items = [
        'log_services = true',
        'log_errors = true',
    ]

    with act.connect_server(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as srv, act.trace(svc_events = trace_svc_items):
        srv.database.get_statistics(database=act.db.db_path, flags=SrvStatFlag.HDR_PAGES)
        srv.wait()

    # Example of line that must be checked for presense of pattern "<user_who_is_tracing>:<his_role>":
    # service_mgr, (service 00000000042b93c0, tmp_tracing_user:tmp_tracing_role, tcpv6:::1/62338, c:\python3x\python.exe:6808)
    #                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #                                         MUST CONTAIN BOTH USER AND ROLE!!

    p_new = re.compile( r'service_mgr.*\s+%s:%s,.*' % (tmp_user.name, tmp_role.name), re.IGNORECASE)
    p_old = re.compile( r'service_mgr.*\s+%s,.*' % tmp_user.name, re.IGNORECASE)

    for line in act.trace_log:
        #if 'service_mgr' in line:
        if 'service_mgr' in line and tmp_user.name in line:
            if p_new.search(line):
                print('EXPECTED output found in the trace log')
            elif p_old.search(line):
                print('ERROR: trace output contains only USER, without ROLE.')
            else:
                print('ERROR: line format in the trace log differs from expected:')
                print(line)
                
    act.stdout = capsys.readouterr().out
    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
