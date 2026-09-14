# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_ts_alter_drop_table
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_ts_alter_drop_table
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = ""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;
    """
    act.isql(switches=['-q', '-n'], input=init_script)

    script = """
    ALTER TABLE TEST_TABLE
    ALTER COLUMN INT_F SET NOT NULL;

    DROP TABLE TEST_TABLE;
    commit;
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', '-n'], input=script)

    assert act.clean_stdout == act.clean_expected_stdout
