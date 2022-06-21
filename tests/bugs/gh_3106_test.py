#coding:utf-8

"""
ID:          issue-3106
ISSUE:       3106
TITLE:       Many indexed reads in a compound index with NULLs
DESCRIPTION:
    BEFORE fix trace log was like this:
    ======
      Table         Natural     Index
      *******************************
      RDB$DATABASE        1
      TEST_TABLE                    3 <<< this line must NOT present now.
    ======
    AFTER fix trace must contain line only for RDB$DATABASE in the table statistics section.

    Confirmed bug on 4.0.0.2451: trace statistics contain line with three indexed reads for test table.
    Checked on 4.0.0.2453 SS/CS: all OK, there are no indexed reads on test table in the trace log.
JIRA:        CORE-2709
FBTEST:      bugs.gh_3106
NOTES:
    [21.06.2022] pzotov
    Checked on 4.0.1.2692, 5.0.0.509.
"""

import locale
import re
import pytest
from firebird.qa import *

init_script = '''
    recreate table test_table (
        id1 int,
        id2 int,
        id3 int
    );
    commit;

    insert into test_table (id1, id2, id3) values (1, 1, null);
    insert into test_table (id1, id2, id3) values (1, 2, null);
    insert into test_table (id1, id2, id3) values (1, 3, null);
    insert into test_table (id1, id2, id3) values (2, 1, null);
    insert into test_table (id1, id2, id3) values (2, 2, null);
    insert into test_table (id1, id2, id3) values (2, 3, null);
    commit;

    create index test_table_idx1 on test_table (id1,id2,id3);
    commit;
'''

db = db_factory(init = init_script)

act = python_act('db', substitutions=[('[ \t]+', ' ')])

FOUND_EXPECTED_TAB_HEAD_MSG = 'Found table statistics header.'
FOUND_EXPECTED_RDB_STAT_MSG = 'Found expected line for rdb$database.'

expected_stdout_trace = f"""
    {FOUND_EXPECTED_TAB_HEAD_MSG}
    {FOUND_EXPECTED_RDB_STAT_MSG}
"""


#@pytest.mark.version('>=4.0')
@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    trace_cfg_items = [
        'time_threshold = 0',
        'log_statement_finish = true',
        'print_perf = true',
    ]

    sql_run='''
      set list on;
      select 1 as dummy from rdb$database r left join test_table t on t.id1 = 1 and t.id2 is null;
    '''

    with act.trace(db_events = trace_cfg_items, encoding=locale.getpreferredencoding()):
        act.isql(input = sql_run, combine_output = True)

    p_tablestat_head = re.compile('Table\\s+Natural\\s+Index', re.IGNORECASE)
    p_tablestat_must_found = re.compile('rdb\\$database\\s+\\d+', re.IGNORECASE)
    p_tablestat_must_miss = re.compile('test_table\\s+\\d+', re.IGNORECASE)

    for line in act.trace_log:
        if p_tablestat_head.search(line):
            print( FOUND_EXPECTED_TAB_HEAD_MSG )
        elif p_tablestat_must_found.search(line):
            print( FOUND_EXPECTED_RDB_STAT_MSG )
        elif p_tablestat_must_miss.search(line):
            print( '### FAILED ### found UNEXPECTED line:')
            print(line.strip())

    act.expected_stdout = expected_stdout_trace
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
