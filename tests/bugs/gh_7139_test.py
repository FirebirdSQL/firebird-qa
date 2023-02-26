#coding:utf-8
"""
ID:          issue-7139
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7139
TITLE:       With multiple trace sessions user may receive trace events related to engine's requests
DESCRIPTION: 
    Test launces TWO trace sessions: one using FB utility 'fbsvcmgr' and second using firebird-qa ("with act.trace: ...").
    ID of trace session that was launched via fbsvcmgr is stored in order to have ability to stop it (again using fbsvcmgr).
    Trace session #2 (that is launched using firebird-qa) is performed in context manager, and we run ISQL there with trivial requirement
    just to make QUIT after connection establishing.
    Trace #2 must NOT issue any messages after that (with exception of 'SET TRANSACTION' which is suppressed by appropriate exclude_filer).
    ::: NB :::
    Timeout about 1.1 second is required after each launching of FB utility fbsvcmgr otherwise either trace session ID can remain None or
    we can encounter with 'WindowsError: [Error 32] The process cannot access the file because it is being used by another process' on
    attempt to delete trace log after 'with' block ends (fbsvcmgr made requests to Services API with interval =  1.0 second).
NOTES:
    [26.02.2023] pzotov
    Confirmed problem on: 5.0.0.514, 4.0.1.2735, got in trace (as reaction on connect + quit):
        select RDB$RELATION_NAME from RDB$USER_PRIVILEGES where RDB$USER = ? and RDB$PRIVILEGE = 'M' and RDB$USER_TYPE = 8 and RDB$OBJECT_TYPE = 13
    Checked on 5.0.0.518 SS/CS; 4.0.1.2736 SS/CS -- all fine: no any message will be issued when two trace sessions exist and we do connect plus quit.
"""

import pytest
import platform
from firebird.qa import *
from pathlib import Path
import subprocess
import time
 
db = db_factory()
act = python_act('db')

tmp_trace_cfg = temp_file('test_trace_and_trivial_actions.cfg')
tmp_trace_log = temp_file('test_trace_and_trivial_actions.log')
 
expected_stdout = """
"""
 
test_script = """
    quit;
"""
 
#-------------------------------------------------------------------------

def get_external_trace_id(act: Action, a_what_to_check, a_ext_trace_session_name):
    v_fbsvcmgr_trace_sess_id = -1
    with act.connect_server() as srv:
        # 1 ::: TraceSession(id=1, user='SYSDBA', timestamp=datetime.datetime(2023, 2, 26, 14, 52, 24), name='trc_gh_7139', flags=['active', ' trace'])
        # 2 ::: TraceSession(id=2, user='SYSDBA', timestamp=datetime.datetime(2023, 2, 26, 14, 53, 58), name='', flags=['active', ' trace'])
        for k,v in srv.trace.sessions.items():
            if v.name == a_ext_trace_session_name:
                v_fbsvcmgr_trace_sess_id = v.id

    msg_prefix = 'Required trace session (launched by fbsvcmgr utility)'
    if a_what_to_check == 'running':
        assert v_fbsvcmgr_trace_sess_id > 0,  msg_prefix + ' NOT found.'
    elif a_what_to_check == 'stopped':
        assert v_fbsvcmgr_trace_sess_id < 0,  msg_prefix + ' WAS NOT DROPPED.'

    return v_fbsvcmgr_trace_sess_id     

#-------------------------------------------------------------------------

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_trace_cfg: Path, tmp_trace_log: Path, capsys):

    # C:\temp\pytest-of-PashaZ\pytest-513\test_10\TEST.FDB
    #    database=[\\\\/]{act.db.db_path}
    trace_txt = f"""
        database=%[\\\\/]{act.db.db_path.name}
        {{
            enabled = true
            log_initfini = false
            log_errors = true
            log_statement_finish = true
            time_threshold = 0
        }}
    """

    tmp_trace_cfg.write_text(trace_txt)

    EXTERNAL_TRC_SESSION_NAME = 'trc_gh_7139'
    MAX_WAIT_FOR_TRACE_STOP = 30

    with tmp_trace_log.open('w') as f_log:
        # EXPLICIT call of FB utility 'fbsvcmgr':
        p = subprocess.Popen( [ act.vars['fbsvcmgr'],
                                'localhost:service_mgr',
                                'user', act.db.user,
                                'password', act.db.password,
                                'action_trace_start',
                                'trc_name', EXTERNAL_TRC_SESSION_NAME,
                                'trc_cfg', tmp_trace_cfg
                              ], 
                              stdout = f_log, stderr = subprocess.STDOUT
                            )
        time.sleep(1.1)

        
        trc_items_list = [
                 'log_initfini = false',
                 'log_errors = true',
                 'log_statement_finish = true',
                 'time_threshold = 0',
                 'exclude_filter="(set transaction)"',
                 ]

        
        with act.trace(db_events=trc_items_list):
            act.isql(switches=['-q'], input=test_script, combine_output = True)

        # ID os trace session that we have started usign FB utility fbsvcmgr:
        v_fbsvcmgr_trace_sess_id = get_external_trace_id(act, 'running', EXTERNAL_TRC_SESSION_NAME)

        q = subprocess.run( [ act.vars['fbsvcmgr'],
                                   'localhost:service_mgr',
                                   'user', act.db.user,
                                   'password', act.db.password,
                                   'action_trace_stop',
                                   'trc_id', str(v_fbsvcmgr_trace_sess_id)
                                   ], 
                                   stdout = f_log,
                                   stderr = subprocess.STDOUT,
                                   timeout = MAX_WAIT_FOR_TRACE_STOP
                                 )

        if q.returncode:
            p.terminate()
        assert q.returncode == 0
        
        time.sleep(1.1)

        v_fbsvcmgr_trace_sess_id = get_external_trace_id(act, 'stopped', EXTERNAL_TRC_SESSION_NAME)

        act.expected_stdout = expected_stdout
        act.trace_to_stdout()
        assert act.clean_stdout == act.clean_expected_stdout

