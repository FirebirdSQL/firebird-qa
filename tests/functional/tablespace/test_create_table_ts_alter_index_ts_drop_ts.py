# coding:utf-8

"""
ID:          functional.tablespace.autoddl_off.test_create_table_ts_alter_index_ts_drop_ts
TITLE:       functional.tablespace.autoddl_off.create_table_ts_alter_index_ts_drop_ts
DESCRIPTION:
NOTES:       Test is currently being skipped because the DROP WITH INCLUDING CONTENTS functionality is not supported.
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = ""


@pytest.mark.skip("Disables: see notes")
@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    for autoddl in (True, False):
        if autoddl:
            commit = 'commit;'
            isql_switches = ['-q']
        else:
            commit = ''
            isql_switches = ['-q', '-n']
        
        ts1_file = tmp_path / 'tablespace1.dat'
        ts1_file.unlink(missing_ok=True)
        ts2_file = tmp_path / 'tablespace2.dat'
        ts2_file.unlink(missing_ok=True)

        script = f"""
        CREATE TABLESPACE TS1 FILE '{ts1_file}';
        {commit}
        CREATE TABLESPACE TS2 FILE '{ts2_file}';
        {commit}
        CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
        {commit}

        CREATE INDEX IDX_TEST ON TEST_TABLE (ID);
        {commit}
        ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
        {commit}
        insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
        {commit}
        ALTER INDEX IDX_TEST SET TABLESPACE TS2;
        {commit}
        ALTER INDEX IDX_TEST SET TABLESPACE PRIMARY;
        {commit}
        ALTER INDEX IDX_TEST inactive;
        {commit}
        DROP TABLESPACE TS1 INCLUDING CONTENTS;
        {commit}
        DROP TABLESPACE TS2 INCLUDING CONTENTS;
        commit;
        """
        act.reset()
        act.expected_stdout = expected_stdout
        act.isql(switches=isql_switches, input=script)

        assert act.clean_stdout == act.clean_expected_stdout, f"AUTODDL: {autoddl}"

        cleanup_script = f"""
        DROP TABLE TEST_TABLE;
        commit;
        """
        act.reset()
        act.isql(switches=['-q'], input=cleanup_script)
