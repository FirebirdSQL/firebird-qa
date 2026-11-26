# coding:utf-8

"""
ID:          functional.tablespace.test_drop_ts
TITLE:       functional.tablespace.drop_ts
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = isql_act('db')

expected_stdout = """
PUBLIC.TEST_TABLE

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE TS1 failed
-cannot delete
-TABLESPACE TS1
-there are 1 dependencies

PUBLIC.TEST_TABLE
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            on_commit = 'commit;'
            off_commit = ''
            isql_switches = ['-q']
        else:
            on_commit = ''
            off_commit = 'commit;'
            isql_switches = ['-q', '-n']

        ts_file = tmp_path / 'tablespace1.dat'
        ts_file.unlink(missing_ok=True)

        init_script = f"""
        CREATE TABLESPACE TS1 FILE '{ts_file}';
        {on_commit}

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
        {on_commit}

        insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
        {on_commit}

        ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
        commit;

        show tables;
        DROP TABLESPACE TS1;
        rollback;

        show tables;
        ALTER TABLE TEST_TABLE SET TABLESPACE PRIMARY;
        {off_commit}
        DROP TABLESPACE TS1;
        """
        act.reset()
        act.isql(switches=isql_switches, combine_output=True, input=init_script)

        act.expected_stdout = expected_stdout
        assert act.clean_stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
