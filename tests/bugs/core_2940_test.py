#coding:utf-8

"""
ID:          issue-3322
ISSUE:       3322
TITLE:       Trace output could contain garbage data left from filtered out statements
DESCRIPTION:
[08.02.2022] pcisar
  Fails on Windows 3.0.8 with unexpected additional output line:
    + 0 records fetched
      1 records fetched
JIRA:        CORE-2940
FBTEST:      bugs.core_2940
"""

import pytest
import platform
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('^((?!records fetched).)*$', '')])

expected_stdout = """
    1 records fetched
"""

test_script = """
    set list on;
    -- statistics for this statement SHOULD appear in trace log:
    select 1 k1 from rdb$database;
    commit;
    -- statistics for this statement should NOT appear in trace log:
    select 2 k2 from rdb$types rows 2 /* no_trace*/;
    -- statistics for this statement should NOT appear in trace log:
    select 3 no_trace from rdb$types rows 3;
    -- statistics for this statement should NOT appear in trace log:
    set term ^;
    execute block returns(k4 int) as
    begin
       for select 4 from rdb$types rows 4 into k4 do suspend;
    end -- no_trace
    ^
    set term ;^
"""

trace = ['log_connections = true',
           'log_transactions = true',
           'log_statement_finish = true',
           'print_plan = true',
           'print_perf = true',
           'time_threshold = 0',
           'exclude_filter = %no_trace%',
           ]

@pytest.mark.skipif(platform.system() == 'Windows', reason='FIXME: see notes')
@pytest.mark.version('>=3.0')
def test_1(act: Action):
    with act.trace(db_events=trace):
        act.isql(switches=['-n'], input=test_script)
    act.expected_stdout = expected_stdout
    act.trace_to_stdout()
    assert act.clean_stdout == act.clean_expected_stdout
