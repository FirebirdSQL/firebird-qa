# coding:utf-8

"""
ID:          functional.tablespace.create_table_ts_create_index
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_table_ts_create_index
"""

import os
import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
substitutions = [('I/O error during .*', 'I/O error during "CreateFile (open)" operation for file'),
                 ('The system cannot find the file specified.', 'No such file or directory')]
act = isql_act('db', substitutions=substitutions)


expected_stderr = """
Statement failed, SQLSTATE = 08001
I/O error during "CreateFile (open)" operation for file "D:\\TESTING\\fbt-repository\\tmp\\tablespace.dat"
-Error while trying to open file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID) TABLESPACE PRIMARY;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;

    SET STATISTICS INDEX IDX_TEST;
    """
    act.isql(switches=['-q'], input=init_script)

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts_file, ts_renamefile)

    script = """
    SET STATISTICS INDEX IDX_TEST;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=script)

    assert act.clean_stderr == act.clean_expected_stderr
