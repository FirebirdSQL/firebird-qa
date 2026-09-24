"""
ID:          functional.tablespace.autoddl_off.drop_if_exists_3
TITLE:       DROP TABLESPACE IF EXISTS
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = isql_act('db')

expected_stderr = """
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-cannot delete
-TABLESPACE TS1
-there are 1 dependencies
"""

expected_stdout = """
PUBLIC.TEST_TABLE
RDB$TABLESPACE_NAME             TS1
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts_file = tmpdir / 'tablespace.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file}';

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL, INT_F INTEGER, FLOAT_F FLOAT, DP_F DOUBLE PRECISION, NUMERIC_F NUMERIC(10,6), TIMESTAMP_F TIMESTAMP, VARCHAR_F VARCHAR(100));

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;
    """
    act.isql(switches=['-q', '-n'], input=init_script)

    check_script = """
        DROP TABLESPACE IF EXISTS TS1;
    commit;
    """
    act.expected_stderr = expected_stderr
    act.isql(switches=['-q', '-n'], input=check_script)
    stderr = act.clean_stderr

    act.reset()
    final_script = """
    show tables;
    set list on;
    SELECT RDB$TABLESPACE_NAME FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME = 'TS1';
    """
    act.isql(switches=['-q', '-n'], input=final_script, combine_output=True)
    stdout = act.clean_stdout

    act.expected_stderr = expected_stderr
    act.expected_stdout = expected_stdout
    assert stderr == act.clean_expected_stderr and stdout == act.clean_expected_stdout
