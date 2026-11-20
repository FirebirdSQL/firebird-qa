# coding:utf-8

"""
ID:          utilites.gbak.tablespace.test_ts_map_non_existing_dir
TITLE:       Restoring tablespace into non-existing directory
DESCRIPTION: 
    Init db:
        Create a test tablespace TS.
        Create a test table. Set the test TS for the table. 
    Backup db.
    Create a tablespace mapping file gbak_ts_map.txt. 
    Specify a path for the restored tablespace with a non-existent directory.
    Restore db using the mapping file.
    Expect an error when restoring db.
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_map_non_existing_dir.py
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [
    ('"/.*gbak_ts', '"gbak_ts'),
    ('".*\\.*gbak_ts', '"gbak_ts'),
    ('The system cannot find the path specified.', 'No such file or directory'),
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
def test_1(act: Action, restored_db: Database, tmp_path: Path):

    ts_filename = 'gbak_ts_map_alias_exists_dir_not_exists.dat'
    ts_original_path = tmp_path / ts_filename

    init_script = f"""
    create tablespace TS FILE '{ts_original_path}';
    commit;

    create table TEST_TABLE1(ID INT UNIQUE, NAME VARCHAR(20) NOT NULL) IN TABLESPACE TS;
    commit;

    insert into TEST_TABLE1 values(1, 'One');
    commit;
    """

    act.isql(switches=['-q'], input=init_script)

    test_db_backup = tmp_path / 'gbak_ts_backup.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    ts_new_file_dir = tmp_path / 'ts_new_dir'
    ts_new_file = ts_new_file_dir / 'gbak_ts.dat'

    ts_map_file = Path(tmp_path / 'gbak_ts_map.txt')
    ts_map_file.write_text(f'TS {ts_new_file}')

    act.expected_stderr = expected_stderr
    act.gbak(switches=['-R', test_db_backup, restored_db.dsn, '-ts_map', ts_map_file])
    assert act.clean_stderr == act.clean_expected_stderr
