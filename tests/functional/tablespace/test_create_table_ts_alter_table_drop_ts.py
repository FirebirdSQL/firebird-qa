# coding:utf-8

"""
ID:          functional.tablespace.create_table_ts_alter_table_drop_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_table_ts_alter_table_drop_ts
NOTES:
    [2025.03.03] Zuev
    Don't delete or replace a file of the test tablespace.
    Only check whether a tablespace can be deleted after objects have been moved from it to another tablespace.
"""

import os
import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = python_act('db')

expected_stdout = """
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
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;


    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE PRIMARY;
    commit;
    """
    act.isql(switches=['-q'], input=init_script)

    script = """
    set list on;
    select * from test_table;
    DROP TABLESPACE TS1;
    """
    act.isql(switches=['-q'], input=script)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
