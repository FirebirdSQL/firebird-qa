# coding:utf-8

"""
ID:             functional.tablespace.test_drop_dependencies_ts_file_not_exists
TITLE:          Test DROP TABLE and DROP INDEX if a tablespace file not exists.
DESCRIPTION:    
    CREATE tablespaces.
    CREATE a table in the first TS.
    CREATE an index in the second TS.
    Rename TS files.
    Try to drop the table.
    Trye to drop the index.
    Expect an error when dropping objects without an existing TS file.
    Restore the TS files.
    Drop objects expecting no errors.
"""

import locale
import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
substitutions = [
    ('I/O error during .*', 'I/O error during "CreateFile (open)" operation for file'),
    ('(-)?The system cannot find the file specified.', ''),
    ('(-)?No such file or directory', ''),
    ('[^\x00-\x7F]+', ''), # find every non-ascii character and suppress its output
    (r'^-\s+.*', ''), # supress output of lines that look like this: "-  ." (they may remain after removing non ascii characters from localized messages)
]
act = isql_act('db', substitutions=substitutions)

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-DROP INDEX "PUBLIC"."TEST_IDX" failed
-I/O error during "open" operation for file "/tmp/pytest-of-anton/pytest-167/test_10/tablespace2.dat"
-Error while trying to open file
-No such file or directory

Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-DROP TABLE "PUBLIC"."TEST_TABLE" failed
-I/O error during "open" operation for file "/tmp/pytest-of-anton/pytest-167/test_10/tablespace1.dat"
-Error while trying to open file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    ts1_file = tmp_path / 'tablespace1.dat'
    ts2_file = tmp_path / 'tablespace2.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    commit;
    CREATE TABLESPACE TS2 FILE '{ts2_file}';
    commit;
    CREATE TABLE TEST_TABLE(ID INT) TABLESPACE TS1;
    commit;
    CREATE INDEX TEST_IDX ON TEST_TABLE(ID) TABLESPACE TS2;
    commit;
    """
    act.reset()
    act.isql(switches=['-q'], input=init_script, io_enc=locale.getpreferredencoding())

    ts1_renamefile = tmp_path / 'ts1_rename.dat'
    ts1_file.rename(ts1_renamefile)
    ts2_renamefile = tmp_path / 'ts2_rename.dat'
    ts2_file.rename(ts2_renamefile)

    script = """
    DROP INDEX TEST_IDX;
    commit;
    DROP TABLE TEST_TABLE;
    commit;
    """
    act.reset()
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=script, io_enc=locale.getpreferredencoding())

    assert act.clean_stderr == act.clean_expected_stderr

    # Restore TS files and try to drop objects
    ts1_renamefile.rename(ts1_file)
    ts2_renamefile.rename(ts2_file)

    script = """
    DROP INDEX TEST_IDX;
    commit;
    DROP TABLE TEST_TABLE;
    commit;
    """
    act.reset()
    act.isql(switches=['-q'], input=script, io_enc=locale.getpreferredencoding())
