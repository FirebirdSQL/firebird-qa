# coding:utf-8

"""
ID:             functional.tablespace.test_drop_ts_file_not_exists
TITLE:          Test DROP TABLESPACE if a tablespace file not exists.
DESCRIPTION:    
    Rename TS file and try to drop TS.
    Expect no errors when dropping TS without an existing file.
NOTES:
    [18.11.2026] Zuev
    Remake the test following the improvements "Don't require an existing tablespace file while dropping it"
    (https://github.com/FirebirdSQL/firebird/commit/85068450cdda886d83638e15d7a25dfc33e47f72).
    Now we can drop a tablespace without an existing tablespace file.
"""

import locale
import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = python_act('db')

expected_stdout = "RDB$TABLESPACE_NAME             TS1"


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    ts_file = tmp_path / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;
    set list on;
    select RDB$TABLESPACE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME = 'TS1';
    """
    act.reset()
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=init_script, io_enc=locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout

    ts_renamefile = tmp_path / 'tablespace_rename.dat'
    ts_file.rename(ts_renamefile)

    script = """
    DROP TABLESPACE TS1;
    commit;
    set list on;
    select RDB$TABLESPACE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME = 'TS1';
    """
    act.reset()
    act.expected_stdout = ""
    act.isql(switches=['-q'], input=script, io_enc=locale.getpreferredencoding())
    assert act.clean_stderr == act.clean_expected_stderr
