#coding:utf-8

"""
ID:          issue-2343
ISSUE:       2343
TITLE:       Better diagnostic when 'Missing security context'
DESCRIPTION:
    ::: NB :::
    List of AuthClient plugins must contain Win_Sspi in order to reproduce this test expected results.
    Otherwise firebird.log will not contain any message like "Available context(s): ..."
    Because of this, test marked as to be performed on WINDOWS only.
JIRA:        CORE-6362
FBTEST:      bugs.core_6362
NOTES:
    [20.06.2022] pzotov
    Message about missed sec. context will raise if we make undefined ISC_* variables and try to connect.
    Confirmed missed info in FB 3.0.6.33301: firebird.log remains unchanged (though ISQL issues expected message).
    Checked on 4.0.1.2692, 3.0.8.33535.
"""

import os
import locale
from difflib import unified_diff
import pytest
from firebird.qa import *

for v in ('ISC_USER','ISC_PASSWORD'):
    try:
        del os.environ[ v ]
    except KeyError as e:
        pass

db = db_factory()

substitutions = [ ( '^((?!context).)*$', ''),
                  ( 'Missing security context(\\(s\\))?( required)? for .*', 'Missing security context'),
                  ( 'Available context(\\(s\\))?(:)? .*', 'Available context'),
                  ( '[\t ]+', ' '),
                ]

act = python_act('db', substitutions = substitutions)

expected_fb_log_diff = """
    + Missing security context
    + Available context
"""

expected_stderr_isql = """
    Statement failed, SQLSTATE = 28000
    Missing security context for TEST.FDB
"""
@pytest.mark.version('>=3.0.7')
@pytest.mark.platform('Windows')
def test_1(act: Action, capsys):
    with act.connect_server(encoding=locale.getpreferredencoding()) as srv:
        srv.info.get_log()
        fb_log_init = srv.readlines()

    act.expected_stderr = expected_stderr_isql
    act.isql(switches=['-q'], input = 'quit;', credentials = False)
    assert act.clean_stderr == act.clean_expected_stderr
    act.reset()

    with act.connect_server(encoding=locale.getpreferredencoding()) as srv:
        srv.info.get_log()
        fb_log_curr = srv.readlines()
 

    for line in unified_diff(fb_log_init, fb_log_curr):
        if line.startswith('+'):
            print(line.strip())

    act.expected_stdout = expected_fb_log_diff
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

