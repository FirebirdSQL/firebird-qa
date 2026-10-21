# coding:utf-8

"""
ID:             functional.tablespace.drop_ts_file_not_exists
TITLE:          Test DROP TABLESPACE if a tablespace file not exists.
DESCRIPTION:    
    Rename TS file and try to drop TS.
    We cannot drop TS without existing file and expect an error.
NOTES:
    [21.10.2026] pzotov
    Adjusted 'substitutions' list to be independent on OS localization.
    Checked on 6.0.0.2405-6b29da9
"""
import locale
import os
import pytest
from pathlib import Path
from firebird.qa import *

substitutions = [
        ('file ".*tablespace.dat"', 'file "tablespace.dat"'),
        ('"CreateFile \\(open\\)"', '"open"'),
        ('The system cannot find the file specified.', ''),
        ('[^\x00-\x7F]+', ''), # find every non-ascii character and suppress its output
        (r'^-\s+.*', ''), # supress output of lines that look like this: "-  ." (they may remain after removing non ascii characters from localized messages)
]

db = db_factory()
act = python_act('db', substitutions=substitutions)

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-I/O error during "open" operation for file "/tmp/pytest-of-root/pytest-129/test_10/tablespace.dat"
-Error while trying to open file
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;
    """
    act.isql(switches=['-q'], input=init_script, combine_output=True, io_enc=locale.getpreferredencoding())
    assert act.return_code ==0 and act.clean_stdout == ''
    act.reset()

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts_file, ts_renamefile)

    script = """
    DROP TABLESPACE TS1;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=script, io_enc=locale.getpreferredencoding())
    assert act.clean_stderr == act.clean_expected_stderr
