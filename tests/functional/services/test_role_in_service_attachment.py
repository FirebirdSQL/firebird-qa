#coding:utf-8
"""
ID:          services.role-in-service-attachment
TITLE:       Check that trace plugin shows ROLE used in service attachment. Format: USER[:ROLE]
DESCRIPTION:
  See: https://github.com/FirebirdSQL/firebird/commit/dd241208f203e54a9c5e9b8b24c0ef24a4298713
FBTEST:      functional.services.role_in_service_attachment

NOTES:
    [30.07.2022] pzotov
    Current version of QA plugin *does* allow to specify user/password/role when we connect to Services API and launch trace.
    But actually this data is not used in by plugin when it launched trace, see 'def trace_thread'.
    It seems that 'with act.connect_server(...)' invocation must use these parameters also, otherwise trace log shows that
    it was started by SYSDBA.
    Sent report to pcisar, 30.07.2022 18:33. Waiting for confirmation or other solution.

    Checked on 4.0.1.2692, 5.0.0.591
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

expected_stdout = 'SUCCESS: found expected line format in the trace log: <USER>:<ROLE>'

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_user: User, tmp_role:Role, capsys):

    init_script = \
    f'''
        set wng off;
        set bail on;
        revoke all on all from {tmp_user.name};
        commit;
        -- Trace other users' attachments
        alter role {tmp_role.name} set system privileges to TRACE_ANY_ATTACHMENT;
        commit;
        grant default {tmp_role.name} to user {tmp_user.name};
        commit;
    '''
    act.isql(switches=['-q'], input=init_script)

    trace_svc_items = [
        'log_services = true',
        'log_errors = true',
    ]

    with act.connect_server(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as srv, \
         act.trace(svc_events = trace_svc_items, user = tmp_user.name, password = tmp_user.password, role = tmp_role.name):
        srv.wait()


    # We want to found line like this:
    # service_mgr, (Service 00000000015A5940, TMP_TRACING_USER:TMP_TRACING_ROLE, TCPv6:::1/63348, C:\python3x\python.exe:21420)

    p_new = re.compile( r'service_mgr.*\s+%s:%s,.*' % (tmp_user.name, tmp_role.name), re.IGNORECASE)
    p_old = re.compile( r'service_mgr.*\s+%s,.*' % tmp_user.name, re.IGNORECASE)

    for line in act.trace_log:
        if 'service_mgr' in line:
            if tmp_user.name in line:
                if p_new.search(line):
                    print( expected_stdout )
                elif p_old.search(line):
                    print('ERROR: trace output contains only USER, without ROLE.')
                else:
                    print('ERROR: line format in the trace log differs from expected:')
                    print(line)
            else:
                if 'SYSDBA' in line:
                    print('ERROR: connect to Services API for trace is still performed by SYSDBA:')
                    print(line)
            break

    act.stdout = capsys.readouterr().out
    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
