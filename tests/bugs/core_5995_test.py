#coding:utf-8

"""
ID:          issue-6245
ISSUE:       6245
TITLE:       Creator user name is empty in user trace sessions
DESCRIPTION:
  We create trivial config for trace, start session and stop it.
  Trace list must contain string: '  user: SYSDBA ' (without apostrophes).
  We search this by string using pattern matching: such line MUST contain at least two words
  (it was just 'user:' before this bug was fixed).
JIRA:        CORE-5995
FBTEST:      bugs.core_5995
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

trace = ['log_initfini = false',
         'time_threshold = 0',
         'log_statement_finish = true',
         ]

@pytest.mark.trace
@pytest.mark.version('>=3.0.5')
def test_1(act: Action):
    with act.trace(db_events=trace), act.connect_server() as srv:
        assert len(srv.trace.sessions) == 1
        for session in srv.trace.sessions.values():
            assert session.user == 'SYSDBA'
