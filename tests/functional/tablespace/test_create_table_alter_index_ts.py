# coding:utf-8

"""
ID:          n/a
TITLE:       functional.tablespace.autoddl_off.create_table_alter_index_ts
DESCRIPTION:
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


db = db_factory()
substitutions = [
    ('I/O error during .*', 'I/O error during "CreateFile (open)" operation for file'),
    ('The system cannot find the file specified.', ''),
    ('[^\x00-\x7F]+', ''), # find every non-ascii character and suppress its output
    (r'^-\s+.*', ''), # supress output of lines that look like this: "-  ." (they may remain after removing non ascii characters from localized messages)
]
act = isql_act('db', substitutions=substitutions)

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-ALTER INDEX "PUBLIC"."IDX_TEST" failed
-I/O error during "CreateFile (open)" operation for file "D:\\TESTING\\fbt-repository\\tmp\\tablespace.dat"
-Error while trying to open file
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID);

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');

    ALTER INDEX IDX_TEST SET TABLESPACE TO TS1;

    ALTER INDEX IDX_TEST inactive;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=init_script, combine_output=True, io_enc=locale.getpreferredencoding())

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts_file, ts_renamefile)

    test_script = """
    ALTER INDEX IDX_TEST active;
    commit;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q', '-n'], input=test_script, io_enc=locale.getpreferredencoding())

    assert act.clean_stderr == act.clean_expected_stderr
