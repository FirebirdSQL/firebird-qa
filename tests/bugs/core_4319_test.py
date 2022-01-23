#coding:utf-8

"""
ID:          issue-4642
ISSUE:       4642
TITLE:       Engine crashes when trace config contains line "connection_id=NN" and we attempt to connect to non-existent database/alias
DESCRIPTION:
NOTES:
[15.1.2022] pcisar
  This test fails on localized Windows due to encoding error and other
  expected output differences, so we skip it for now.
JIRA:        CORE-4319
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stderr = """
Rolling back work.
Statement failed, SQLSTATE = 08001
I/O error during "open" operation for file "some_non_existent"
-Error while trying to open file
-No such file or directory
Use CONNECT or CREATE DATABASE to specify a database
Command error: show database
Cannot get server version without database connection
"""

trace = ['time_threshold = 0',
         'log_errors = true',
         'connection_id = 1234',
         'log_connections = true',
         ]

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    if act.platform == 'Windows':
        pytest.skip("Windows: See note in test")
    with act.trace(db_events=trace):
        act.expected_stderr = expected_stderr
        act.isql(switches=['-n'],
                   input="connect 'localhost:some_non_existent' user 'SYSDBA' password 'masterkey'; show database; show version;")
    # check that we are still kicking (via trace exit) and got expected result from isql
    assert act.clean_stderr == act.clean_expected_stderr
