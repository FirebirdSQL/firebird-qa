# coding:utf-8

"""
ID:          functional.tablespace.test_create_table_ts_alter_drop_table
TITLE:       functional.tablespace.create_table_ts_alter_drop_table
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = ""


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

        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
        {commit}

        ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
        {commit}

        insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
        commit;
        """
        act.reset()
        act.isql(switches=isql_switches, input=init_script)

        script = f"""
        ALTER TABLE TEST_TABLE
        ALTER COLUMN INT_F SET NOT NULL;
        {commit}

        DROP TABLE TEST_TABLE;
        commit;
        """
        act.reset()
        act.expected_stdout = expected_stdout
        act.isql(switches=isql_switches, input=script)

        assert act.clean_stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLESPACE TS1;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
