"""
ID:          functional.tablespace.drop_if_exists_2
TITLE:       DROP TABLESPACE IF EXISTS
DESCRIPTION:
"""


import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = isql_act('db')

expected_stdout = """
There are no tables in this database
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL, INT_F INTEGER, FLOAT_F FLOAT, DP_F DOUBLE PRECISION, NUMERIC_F NUMERIC(10,6), TIMESTAMP_F TIMESTAMP, VARCHAR_F VARCHAR(100));
    commit;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;

    show tables;
    DROP TABLE IF EXISTS TEST_TABLE;
    commit;
    """
    act.isql(switches=['-q'], input=init_script, combine_output=True)

    check_script = """
        DROP TABLESPACE IF EXISTS TS1;
        commit;
        """
    act.isql(switches=['-q'], input=check_script)

    final_script = """
    show tables;
    set list on;
    SELECT * FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME = 'TS1';
    """
    act.isql(switches=['-q'], input=final_script, combine_output=True)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
