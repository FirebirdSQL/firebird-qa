#coding:utf-8

"""
ID:          issue-5183
ISSUE:       5183
TITLE:       FBSVCMGR with `action_trace_start` prevents in 3.0 SuperServer from connecting using local protocol
DESCRIPTION:
NOTES:
  This test fails on Windows with "FAILED to find text in trace related to EMBEDDED connect."
JIRA:        CORE-4889
FBTEST:      bugs.core_4889
"""

import pytest
import platform
from firebird.qa import *

db = db_factory()

act = python_act('db')

isq_script = """
set list on;
set count on;
select
    iif(a.mon$remote_protocol is null, 'internal', 'remote') as connection_protocol,
    iif(a.mon$remote_process is null,  'internal', 'remote') as connection_process,
    iif(a.mon$remote_pid     is null,  'internal', 'remote') as connection_remote_pid,
    a.mon$auth_method as auth_method -- should be: 'User name in DPB'
from rdb$database r
left join mon$attachments a on a.mon$attachment_id = current_connection and a.mon$system_flag = 0;
commit;
"""

expected_stdout = """
     OK: found text in trace related to EMBEDDED connect.
     CONNECTION_PROTOCOL             internal
     CONNECTION_PROCESS              internal
     CONNECTION_REMOTE_PID           internal
     AUTH_METHOD                     User name in DPB
     Records affected: 1
"""

trace = ['time_threshold = 0',
         'log_initfini = false',
         'log_errors = true',
         'log_statement_finish = true',
         ]

@pytest.mark.skipif(platform.system() == 'Windows', reason='FIXME: see notes')
@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    with act.trace(db_events=trace):
        act.isql(switches=['-n', '-user', 'tmp$no$such$user$4889', str(act.db.db_path)],
                 connect_db=False, credentials=False, input=isq_script)
    # Process trace log
    i = 0
    for line in act.trace_log:
        if ') EXECUTE_STATEMENT_FINISH' in line:
            i = 1
        if i == 1 and '1 records fetched' in line:
            i = 2
            print("OK: found text in trace related to EMBEDDED connect.")
            break
    if not i == 2:
        print("FAILED to find text in trace related to EMBEDDED connect.")
    print(act.stdout if act.stdout else "FAILED to print log from EMBEDDED connect: log is EMPTY.")
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
