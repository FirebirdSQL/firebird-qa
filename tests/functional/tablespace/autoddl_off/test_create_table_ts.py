# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_ts
"""

import os
import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
substitutions = [('I/O error during .*', 'I/O error during "CreateFile (open)" operation for file'),
                 ('The system cannot find the file specified.', 'No such file or directory')]
act = isql_act('db', substitutions=substitutions)


expected_stdout = """
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer 
RDB$TABLESPACE_NAME             TS1
"""

expected_stderr = """
Statement failed, SQLSTATE = 08001
I/O error during "CreateFile (open)" operation for file 
-Error while trying to open file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100)) TABLESPACE TS1;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;
    """
    act.isql(switches=['-q', '-n'], input=script)

    script = """
    set list on;
    select * from test_table;
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE';
    """
    act.isql(switches=['-q', '-n'], input=script)
    stdout = act.clean_stdout
    act.reset()

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts_file, ts_renamefile)

    script = """
    set list on;
    select * from test_table;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q', '-n'], input=script)
    stderr = act.clean_stderr

    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    assert stdout == act.clean_expected_stdout and stderr == act.clean_expected_stderr
