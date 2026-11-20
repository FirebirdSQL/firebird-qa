# coding:utf-8

"""
ID:          utilites.gbak.tablespace.test_ts_non_existing_dir
TITLE:       Test restore of a database with tablespaces with gbak -ts option
DESCRIPTION:
    Tablespace file directory does not exist.
    Expect an error.
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_non_existing_dir.py
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [
    ('"/.*gbak_ts', '"gbak_ts'),
    ('".*\\.*gbak_ts', '"gbak_ts'),
    ('The system cannot find the path specified.', 'No such file or directory')
]

db = db_factory()
act = python_act('db', substitutions=substitutions)

restored_db = db_factory(filename='restore.fdb', do_not_create=True)

expected_stderr = """
gbak: ERROR:I/O error during "open O_CREAT" operation for file "gbak_ts.dat"
gbak: ERROR:    Error while trying to create file
gbak: ERROR:    No such file or directory
gbak:Exiting before completion due to errors
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, restored_db:Database, tmp_path: Path):

    ts_file = tmp_path / 'gbak_ts.dat'

    script = f"""
    create tablespace TS FILE '{ts_file}';
    commit;

    create table TEST_TABLE1(ID INT UNIQUE, NAME VARCHAR(20) NOT NULL) IN TABLESPACE TS;
    commit;

    insert into TEST_TABLE1 values(1, 'One');
    commit;
    """

    act.isql(switches=['-q'], input=script)

    test_db_backup = tmp_path / 'gbak_ts_backup.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    ts_new_file_dir = tmp_path / 'ts_new_dir'
    ts_new_file = ts_new_file_dir / 'gbak_ts.dat'

    act.expected_stderr = expected_stderr
    act.gbak(switches=['-C', test_db_backup, restored_db.dsn, '-ts', 'TS', ts_new_file])
    assert act.clean_stderr == act.clean_expected_stderr
