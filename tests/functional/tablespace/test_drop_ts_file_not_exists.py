# coding:utf-8

"""
ID:             functional.tablespace.test_drop_ts_file_not_exists
TITLE:          Test DROP TABLESPACE if a tablespace file not exists.
DESCRIPTION:
    Rename TS file and try to drop TS.
    Since commit 85068450cdda886d83638e15d7a25dfc33e47f72 ("Don't require an existing
    tablespace file while dropping it", src/dsql/TablespaceNodes.epp) DROP TABLESPACE
    must NOT open the backing file: it only needs tablespace metadata and its lock.
    Before that commit drop failed with I/O error "Error while trying to open file"
    (SQLSTATE = 08001) when the file was missing; now the drop must SUCCEED and the
    tablespace must disappear from RDB$TABLESPACES.
NOTES:
    [21.10.2026] pzotov
    Adjusted 'substitutions' list to be independent on OS localization.
    Checked on 6.0.0.2405-6b29da9.
    
    [19.11.2026] pzotov
    Test was re-implemented using AI (ZCode) because commit 85068450 intentionally
    changed the behavior: DROP TABLESPACE no more requires existing tablespace file.

    Checked on:
    * 6.0.0.2483-8ecd851 -- FAILED: drop raised I/O error (old behavior),
    * 6.0.0.2488-6158583 (contains commit 85068450) -- passed: drop succeeded.
"""
import locale
import os
import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
substitutions = [
    ('[ \t]+', ' '),
    ('I/O error during .*', 'I/O error during "CreateFile (open)" operation for file'),
    ('(-)?The system cannot find the file specified.', ''),
    ('(-)?No such file or directory', ''),
    ('[^\x00-\x7F]+', ''), # find every non-ascii character and suppress its output
    (r'^-\s+.*', ''), # supress output of lines that look like this: "-  ." (they may remain after removing non ascii characters from localized messages)
]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):

    ts_file = tmpdir / 'tablespace.dat'
    ts_name = 'ts1'.upper()

    init_script = f"""
        create view v_info as select count(*) as ts_count from rdb$tablespaces where rdb$tablespace_name = '{ts_name}';
        create tablespace {ts_name} file '{ts_file}';
        commit;
        create table ts_test(id int) tablespace {ts_name};
        commit;
        alter table ts_test set tablespace primary;
        commit;
    """
    act.isql(switches=['-q'], input=init_script, combine_output=True, io_enc=locale.getpreferredencoding())
    assert act.return_code == 0 and act.clean_stdout == ''
    act.reset()

    assert ts_file.exists(), f'tablespace file was not created: {ts_file}'

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts_file, ts_renamefile)

    script = f"""
        set list on;
        select * from v_info;
        drop tablespace {ts_name};
        commit;
        select * from v_info;
    """

    expected_stdout = """
        TS_COUNT 1
        TS_COUNT 0
    """
   
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=script, combine_output=True, io_enc=locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout

