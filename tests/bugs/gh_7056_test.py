#coding:utf-8

"""
ID:          issue-8168
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8168
TITLE:       Fetching from a scrollable cursor may overwrite user-specified buffer and corrupt memory
DESCRIPTION: Engine did overwrite the user-specified buffer with four more bytes than expected that could corrupt the caller memory.
NOTES:
    [18.07.2024] pzotov
    1. Apropriate script without QA plugin caused crash of Python up to 5.0.0.325 (30-nov-2021).
       Snapshot 5.0.0.326-fd6bf8d (01-dec-2021 08:44) was fixed but only if we run script not under QA plugin.
    2. Despite that fix (fd6bf8d404068417552f9c8d7ae2e232fa860005, 01-dec-2021 11:45), actually all subsequent
       FB snapshots still had a problem until 10-jan-2023: running this test on them caused BUGCHECK
       "internal Firebird consistency check (decompression overran buffer (179), file: sqz.cpp line: 293)"
    3. Eventually problem was solved 10-JAN-2023:
        5.0.0.890-a6ce0ec -- crash
        5.0.0.890-aa847a7 -- OK
    4. Discussed between dimitr, pcisar and pzotov, see letters of 29-30 NOV 2021,
       subj: "firebird-driver & scrollable cursors // misc. tests, requested by dimitr"
    5. Problem appeared only for column with width = 32765 characters, thus DB charset must be single-byte, e.g. win1251 etc.
       Otherwise (with default charset = 'utf8') this test will fail with:
       "SQLSTATE = 54000 / ... or string truncation / -Implementation limit exceeded"

    Checked on 6.0.0.396, 5.0.1.1440
"""
import pytest
from firebird.qa import *

N_WIDTH = 32765

init_script = f"""
    recreate table ts(id int primary key, s varchar({N_WIDTH}));
    insert into ts(id,s) values( 1, lpad('', {N_WIDTH}, 'A') );
    commit;
"""
db = db_factory(init=init_script, charset = 'win1251')
act = python_act('db', substitutions=[('[ \t]+', ' ')])

@pytest.mark.scroll_cur
@pytest.mark.version('>=5.0.0')
def test_1(act: Action, capsys):
    success_msg = 'COMPLETED.'
    with act.db.connect() as con:
        cur = con.cursor()
        cur.open('select id, s from ts order by id')
        cur.fetch_first()
    print(success_msg)

    act.expected_stdout = f"{success_msg}"
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

