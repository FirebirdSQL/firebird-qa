# coding:utf-8
"""
ID:          utilites.gbak.tablespace.tablespace
TITLE:       Restore database with tablespaces without tablespace mapping
DESCRIPTION: 
    Init db:
        Create a test tablespace TS1.
        Create a test table. Set the test TS for the table. 
    Backup db.
    Restore db without using a tablespace mapping.
    Expect an error when restoring db.
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
substitutions = [('original path:.*tablespace1.dat', 'original path: tablespace1.dat')]
act = python_act('db', substitutions=substitutions)

expected_stderr = """
gbak: ERROR:path to tablespace TS1 is not specified (original path: "/testing/fbt-repository/tmp/tablespace1.dat")
gbak:Exiting before completion due to errors
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    ts1_file = tmp_path / 'tablespace1.dat'
    restore_dsn = tmp_path / 'test_db_restore.fdb'
    backup_dsn = tmp_path / 'test_db_backup.fbk'

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    commit;

    CREATE TABLE TEST_TABLE(ID BIGINT NOT NULL,INT_F INTEGER,FLOAT_F FLOAT,DP_F DOUBLE PRECISION,NUMERIC_F NUMERIC(10,6),TIMESTAMP_F TIMESTAMP,VARCHAR_F VARCHAR(100));
    commit;

    ALTER TABLE TEST_TABLE SET TABLESPACE TS1;
    commit;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;
    """
    act.isql(switches=['-q'], input=script)

    act.gbak(switches=['-B', act.db.dsn, backup_dsn])

    act.expected_stderr = expected_stderr
    act.gbak(switches=['-C', backup_dsn, restore_dsn])
    error = act.stderr

    act.stderr = error
    assert act.clean_stderr == act.clean_expected_stderr
