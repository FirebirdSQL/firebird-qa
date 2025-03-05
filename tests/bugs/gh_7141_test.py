#coding:utf-8

"""
ID:          issue-7141
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7141
TITLE:       Services manager breaks long lines into 1023 bytes portions when using isc_info_svc_line in Service::query()
DESCRIPTION:
    Test invokes fbsvcmgr utility with requirement to start sepaarate trace session which will have long name.
    This name is stored in variable LONG_NAME_OF_TRACE_SESSION and its maximal len currently is 16254.
    Then we try to find this name in two ways:
        * using act.connect_server().trace.sessions.items();
        * using fbsvcmgr action_trace_list.
    Both way must return info which contains <LONG_NAME_OF_TRACE_SESSION> without line breaking (this is what was fixed).
NOTES:
    Confirmed bug on 4.0.1.2735, 3.0.10.33570: name of session did contain LF characters in its middle points.
    Confirmed problem on 5.0.0.418 - but only for console FB utility (fbsvcmgr), and NOT for usage firebird-QA framework
    (it causes BUGCHECK "decompression overran buffer (179), file: sqz.cpp line: 293" on test teardown phase).
    Checked on 6.0.0.363, 5.0.1.1408, 4.0.5.3103, 3.0.12.33744
"""

import pytest
import platform
import re
from firebird.qa import *
from pathlib import Path
import subprocess
import time

#db = db_factory(async_write = False)
db = db_factory()
act = python_act('db')

tmp_trace_cfg = temp_file('test_trace_7141.cfg')
tmp_trace_log = temp_file('test_trace_7141.log')

MAX_WAIT_FOR_TRACE_STOP = 10
TRC_SESSION_NAME_PREFIX = 'gh_7141_'
TRC_SESSION_NAME_MAX_LEN = 16254

# 65000 100000 -->  FileNotFoundError: [WinError 206]  The filename or extension is too long // in localized form!
# 32000  --> AssertionError: Could not find trace session to be stopped in {act.connect_server().trace.sessions.items()=} // None
LONG_NAME_OF_TRACE_SESSION = (TRC_SESSION_NAME_PREFIX * 10000000)[:TRC_SESSION_NAME_MAX_LEN]
EXPECTED_MSG1 = 'Success: found trace session name in act.connect_server().trace.sessions.items()'
EXPECTED_MSG2 = 'Success: found trace session name in the result of fbsvcmgr action_trace_list'

@pytest.mark.trace
@pytest.mark.version('>=3.0.10')
def test_1(act: Action, tmp_trace_cfg: Path, tmp_trace_log: Path, capsys):

    trace_txt = f"""
        database=%[\\\\/]{act.db.db_path.name}
        {{
            enabled = true
            log_initfini = false
        }}
    """

    tmp_trace_cfg.write_text(trace_txt)
    trace_session_id = -1
    trace_session_nm = ''

    with tmp_trace_log.open('w') as f_log:
        # EXPLICIT call of FB utility 'fbsvcmgr':
        p = subprocess.Popen( [ act.vars['fbsvcmgr'],
                                'localhost:service_mgr',
                                'user', act.db.user,
                                'password', act.db.password,
                                'action_trace_start',
                                'trc_name', LONG_NAME_OF_TRACE_SESSION,
                                'trc_cfg', tmp_trace_cfg
                              ], 
                              stdout = f_log, stderr = subprocess.STDOUT
                            )
        time.sleep(1.1)

        q1 = subprocess.run( [ act.vars['fbsvcmgr'],
                              'localhost:service_mgr',
                              'user', act.db.user,
                              'password', act.db.password,
                              'action_trace_list',
                            ], 
                            stdout = f_log, stderr = subprocess.STDOUT
                         )

        assert q1.returncode == 0

        with act.connect_server() as srv:
            # K = 1
            # V = TraceSession(id=1, user='SYSDBA', timestamp=..., name=<LONG_NAME_OF_TRACE_SESSION>, flags=['active', ' trace'])
            for k,v in srv.trace.sessions.items():
                if v.flags[0] == 'active' and v.name.startswith(TRC_SESSION_NAME_PREFIX):
                    trace_session_id = v.id
                    trace_session_nm = v.name
            
        assert trace_session_id > 0, f'Could not find trace session to be stopped in {act.connect_server().trace.sessions.items()=}'

        q2 = subprocess.run( [ act.vars['fbsvcmgr'],
                              'localhost:service_mgr',
                              'user', act.db.user,
                              'password', act.db.password,
                              'action_trace_stop',
                              'trc_id', str(trace_session_id)
                            ], 
                            stdout = f_log, stderr = subprocess.STDOUT,
                            timeout = MAX_WAIT_FOR_TRACE_STOP
                         )

        time.sleep(1.1)
        if not p.poll():
            p.terminate()
        assert q2.returncode == 0
    
    if trace_session_nm == LONG_NAME_OF_TRACE_SESSION:
        print(EXPECTED_MSG1)
    else:
        print('UNEXPECTED. COULD NOT FIND trace session name in in act.connect_server().trace.sessions.items()')

    p_prefix_in_list = re.compile(f'name(:)?\\s+{TRC_SESSION_NAME_PREFIX}', re.IGNORECASE)

    found_in_trc_list = False
    with tmp_trace_log.open('r') as f_log:
        for line in f_log:
            #if p_prefix_in_list.search(line):
            if LONG_NAME_OF_TRACE_SESSION in line:
                found_in_trc_list = True
                print(EXPECTED_MSG2)
                break

    if not found_in_trc_list:
        print('Check result of fbsvcmgr action_trace_list:')
        with tmp_trace_log.open('r') as f:
            trace_lines = [ x for x in f.read().splitlines() if x.split() ]
            for i, x in enumerate(trace_lines):
                print(f'line {i}, length = {len(x.rstrip())}: >' + x.rstrip() + '<')

    act.expected_stdout = f"""
        {EXPECTED_MSG1}
        {EXPECTED_MSG2}
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
