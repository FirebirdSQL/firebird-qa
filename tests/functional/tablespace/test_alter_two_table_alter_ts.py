# coding:utf-8

"""
ID:          functional.tablespace.alter_two_table_alter_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.alter_two_table_alter_ts
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
substitutions = [('Tablespace "TS1" alteration error. File.*does not exist.',
                  'Tablespace "TS1" alteration error. File')]
act = isql_act('db', substitutions=substitutions)

expected_stdout = """
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer
ID                              343
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'

    test_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
    commit;
    CREATE TABLE TEST_TABLE2(ID INTEGER);
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;

    ALTER TABLE TEST_TABLE2 SET TABLESPACE TS1;
    commit;

    insert into test_table2 values (343);
    commit;


    set list on;
    select * from test_table;
    select * from test_table2;
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=test_script)

    assert act.clean_stdout == act.clean_expected_stdout
