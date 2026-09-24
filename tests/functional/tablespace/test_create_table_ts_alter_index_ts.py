# coding:utf-8

"""
ID:          functional.tablespace.create_table_ts_alter_index_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_table_ts_alter_index_ts
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
unsuccessful metadata update
-ALTER INDEX "PUBLIC"."IDX_TEST" failed
-I/O error during "CreateFile (open)" operation for file "D:\\TESTING\\fbt-repository\\tmp\\tablespace.dat"
-Error while trying to open file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    commit;
    CREATE TABLESPACE TS2 FILE '{ts2_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
    commit;


    CREATE INDEX IDX_TEST ON TEST_TABLE (ID);
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;

    ALTER INDEX IDX_TEST SET TABLESPACE TS2;
    commit;
    """
    act.isql(switches=['-q'], input=script)

    script = """
    ALTER INDEX IDX_TEST inactive;
    """
    act.isql(switches=['-q'], input=script)

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts2_file, ts_renamefile)

    script = """
    ALTER INDEX IDX_TEST active;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q'], input=script)

    assert act.clean_stderr == act.clean_expected_stderr
