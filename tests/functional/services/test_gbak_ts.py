# coding:utf-8
"""
ID:          functional.services.gbak_ts
TITLE:       Service Manager restore with tablespace path mapping
DESCRIPTION: Verifies database restore via Service Manager using gbak with -res_ts_path option:
             1) error when -res_ts_path is specified without required parameters,
             2) error when tablespace TS1 path is not specified,
             3) successful restore when paths for all tablespaces are correctly provided.
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
substitutions = [
    ('/.*tablespace1.dat', 'tablespace1.dat'),
    ('.:.*tablespace1.dat', 'tablespace1.dat'),
    ('/.*tablespace2.dat', 'tablespace2.dat'),
    ('.:.*tablespace2.dat', 'tablespace2.dat')
]
act = python_act('db', substitutions=substitutions)

restored_db = db_factory(filename="test_db_restore.fdb", charset='UTF8', do_not_create=True)

expected_stdout = """
ID                              123
INT_F                           345
FLOAT_F                         34.23
DP_F                            56.45000000000000
NUMERIC_F                       87.560000
TIMESTAMP_F                     1983-02-01 00:00:00.0000
VARCHAR_F                       summer

RDB$TABLESPACE_NAME             TS1
RDB$FILE_NAME                   tablespace1.dat
RDB$TABLESPACE_NAME             TS2
RDB$FILE_NAME                   tablespace2.dat
"""

expected_stderr = """
Invalid or missing parameter for switch -res_ts_path

path to tablespace TS1 is not specified (original path: tablespace1.dat")
-Exiting before completion due to errors
"""


@pytest.mark.version('>=6')
def test_1(act: Action, restored_db: Database, tmp_path: Path):
    ts1_file = tmp_path / 'tablespace1.dat'
    ts1_restore = tmp_path / 'tablespace1_restore.dat'
    ts2_file = tmp_path / 'tablespace2.dat'
    ts2_restore = tmp_path / 'tablespace2_restore.dat'
    backup_dsn = tmp_path / 'test_db_backup.fbk'

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    CREATE TABLESPACE TS2 FILE '{ts2_file}';
    commit;

    CREATE TABLE TEST_TABLE(
        ID BIGINT NOT NULL,
        INT_F INTEGER,
        FLOAT_F FLOAT,
        DP_F DOUBLE PRECISION,
        NUMERIC_F NUMERIC(10,6),
        TIMESTAMP_F TIMESTAMP,
        VARCHAR_F VARCHAR(100)
    ) IN TABLESPACE TS1;
    commit;

    insert into test_table values (123, 345, 34.23, 56.45, 87.56, '01.02.1983', 'summer');
    commit;
    """
    act.isql(switches=['-q'], input=script)

    act.reset()
    act.svcmgr(switches=['-action_backup', '-dbname', act.db.db_path, '-bkp_file', backup_dsn])

    # parameter for option -TS is missing
    act.reset()
    act.expected_stderr = expected_stderr
    act.svcmgr(switches=['-action_restore', '-bkp_file', backup_dsn,
               '-dbname', restored_db.db_path, '-res_ts_path'])
    error = act.stderr

    # TS1 not specified
    act.reset()
    act.expected_stderr = expected_stderr
    act.svcmgr(switches=['-action_restore', '-bkp_file', backup_dsn, '-dbname', restored_db.db_path,
               '-res_ts_path', 'TS2', ts2_restore])
    error += act.stderr

    # Normal
    act.reset()
    act.svcmgr(switches=['-action_restore', '-bkp_file', backup_dsn, '-dbname', restored_db.db_path, '-res_replace',
               '-res_ts_path', 'TS1', ts1_restore, '-res_ts_path', 'TS2', ts2_restore])

    check_script = """
    set list on; 
    SELECT * FROM TEST_TABLE;
    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$SYSTEM_FLAG = 0;
    """
    act.isql(switches=['-q'], input=check_script, use_db=restored_db)
    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout

    act.stderr = error
    act.expected_stderr = expected_stderr
    assert act.clean_stderr == act.clean_expected_stderr
