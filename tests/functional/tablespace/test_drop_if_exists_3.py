"""
ID:          functional.tablespace.test_drop_if_exists_3
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
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            commit = 'commit;'
            isql_switches = ['-q']
        else:
            commit = ''
            isql_switches = ['-q', '-n']
        
        ts_file = tmp_path / 'tablespace1.dat'
        ts_file.unlink(missing_ok=True)

        init_script = f"""
        CREATE TABLESPACE TS1 FILE '{ts_file}';
        {commit}

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL, INT_F INTEGER, FLOAT_F FLOAT, DP_F DOUBLE PRECISION, NUMERIC_F NUMERIC(10,6), TIMESTAMP_F TIMESTAMP, VARCHAR_F VARCHAR(100));
        {commit}

        insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
        {commit}

        ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=init_script)

        check_script = """
        DROP TABLESPACE IF EXISTS TS1;
        commit;
        """
        act.reset()
        act.expected_stderr = expected_stderr
        act.isql(switches=isql_switches, input=check_script)
        stderr = act.clean_stderr

        act.reset()
        final_script = """
        show tables;
        set list on;
        SELECT RDB$TABLESPACE_NAME FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME = 'TS1';
        """
        act.reset()
        act.isql(switches=isql_switches, input=final_script, combine_output=True)
        stdout = act.clean_stdout

        act.expected_stderr = expected_stderr
        act.expected_stdout = expected_stdout
        assert stderr == act.clean_expected_stderr and stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        DROP TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
