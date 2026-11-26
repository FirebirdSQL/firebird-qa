#coding:utf-8

"""
ID:          functional.tablespace.test_create_table_ts_create_index_ts_default
TITLE:       functional.tablespace.autoddl_off.create_table_ts_create_index_ts_default
DESCRIPTION:
NOTES:
    [21.10.2026] pzotov
    Adjusted 'substitutions' list to be independent on OS localization.
    Checked on 6.0.0.2405-6b29da9
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

expected_stdout = """
RDB$TABLESPACE_NAME             TS1
"""

expected_stderr = """
Statement failed, SQLSTATE = 08001
I/O error during "CreateFile (open)" operation for file "D:\\TESTING\\fbt-repository\\tmp\\tablespace.dat"
-Error while trying to open file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            commit = 'commit;'
            isql_switches = ['-q']
        else:
            commit = ''
            isql_switches = ['-q', '-n']
        
        ts_file = tmp_path / 'tablespace1.dat'
        ts_file.unlink(missing_ok=True)

        script = f"""
        CREATE TABLESPACE TS1 FILE '{ts_file}';
        {commit}

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100)) TABLESPACE TS1;
        {commit}

        CREATE INDEX IDX_TEST ON TEST_TABLE (ID);

        insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
        {commit}

        SET STATISTICS INDEX IDX_TEST;
        set list on;
        select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IDX_TEST';
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=script, io_enc=locale.getpreferredencoding())
        stdout = act.clean_stdout

        ts_renamefile = tmp_path / 'tablespace_rename.dat'
        ts_renamefile.unlink(missing_ok=True)
        ts_file.rename(ts_renamefile)

        script = """
        SET STATISTICS INDEX IDX_TEST;
        """
        act.reset()
        act.expected_stderr = expected_stderr
        act.isql(switches=isql_switches, input=script, io_enc=locale.getpreferredencoding())
        stderr = act.clean_stderr
        
        act.expected_stdout = expected_stdout
        assert stdout == act.clean_expected_stdout and stderr == act.clean_expected_stderr, f"AUTODDL: {autoddl}"

        # Restore TS file before cleanup
        ts_renamefile.rename(ts_file)

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        DROP TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
