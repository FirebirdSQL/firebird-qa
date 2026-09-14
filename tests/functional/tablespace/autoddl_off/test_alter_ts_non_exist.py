# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.alter_ts_non_exist
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.autoddl_off.alter_ts_non_exist
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
substitutions = [('Tablespace file.*does not exist',
                  'Tablespace file')]
act = isql_act('db', substitutions=substitutions)

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-ALTER TABLESPACE TS1 failed
-Tablespace file "D:\\TESTING\\fbt-repository\\tmp\\tablespace2.dat" does not exist
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
    commit;
    """
    act.isql(switches=['-q', '-n'], input=test_script)

    act.reset()
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q', '-n'], input=f"ALTER TABLESPACE TS1 SET FILE '{ts2_file}';")

    act.expected_stderr = expected_stderr
    assert act.clean_stderr == act.clean_expected_stderr
