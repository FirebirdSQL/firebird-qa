# coding:utf-8

"""
ID:          functional.tablespace.create_table_ts_alter_index_ts_2
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_table_ts_alter_index_ts_2
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
PLAN ("PUBLIC"."TEST_TABLE" INDEX ("PUBLIC"."IDX_TEST"))
ID                              78
INT_F                           87
FLOAT_F                         4.5999999
DP_F                            467.7687000000000
NUMERIC_F                       90.793000
TIMESTAMP_F                     1985-04-15 00:00:00.0000
VARCHAR_F                       autumn
PLAN ("PUBLIC"."TEST_TABLE" INDEX ("PUBLIC"."IDX_TEST"))
ID                              78
INT_F                           87
FLOAT_F                         4.5999999
DP_F                            467.7687000000000
NUMERIC_F                       90.793000
TIMESTAMP_F                     1985-04-15 00:00:00.0000
VARCHAR_F                       autumn
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


    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    insert into test_table values (344, 45, 67.89, 78.898, 78.878, '10.11.1984', 'winter');
    insert into test_table values (78, 87, 4.6, 467.7687, 90.793, '15.04.1985', 'autumn');
    insert into test_table values (94, 145, 7.87, 899.456, 36.57, '08.06.1986', 'spring');
    commit;

    CREATE INDEX IDX_TEST ON TEST_TABLE (ID) TABLESPACE TS1;
    commit;

    set list on;
    set plan on;
    select * from TEST_TABLE where id = 78;

    ALTER INDEX IDX_TEST SET TABLESPACE TS2;
    commit;

    select * from TEST_TABLE where id = 78;
    commit;
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=script)

    assert act.clean_stdout == act.clean_expected_stdout
