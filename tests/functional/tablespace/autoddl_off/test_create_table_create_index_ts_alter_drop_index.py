# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.create_table_create_index_ts_alter_drop_index
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.create_table_create_index_ts_alter_drop_index
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db',)

expected_stdout = ""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    CREATE TABLESPACE TS2 FILE '{ts2_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID);

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');

    ALTER INDEX IDX_TEST SET TABLESPACE TS2;

    ALTER INDEX IDX_TEST inactive;
    DROP INDEX IDX_TEST;
    commit;
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', '-n'], input=init_script)

    assert act.clean_stdout == act.clean_expected_stdout
