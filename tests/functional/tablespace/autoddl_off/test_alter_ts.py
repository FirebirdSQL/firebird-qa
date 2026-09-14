# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.alter_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.alter_ts
"""

import os
import pytest
import shutil
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    test_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');

    set list on;
    select * from test_table;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=test_script)
    stdout = act.clean_stdout + '\n'

    shutil.copyfile(ts1_file, ts2_file)
    act.isql(switches=['-q', '-n'], input=f"ALTER TABLESPACE TS1 SET FILE TO '{ts2_file}';")

    ts_renamefile = tmpdir / 'tablespace_rename.dat'
    os.rename(ts1_file, ts_renamefile)

    after_rename_script = """
    set list on;
    select * from test_table;
    """
    act.isql(switches=['-q', '-n'], input=after_rename_script)
    stdout += act.clean_stdout

    act.expected_stdout = expected_stdout
    assert stdout == act.clean_expected_stdout
