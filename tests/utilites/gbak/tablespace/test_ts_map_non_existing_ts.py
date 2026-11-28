# coding:utf-8

"""
ID:          utilites.gbak.tablespace.ts_map_non_existing_ts
TITLE:       Test restore of a database with tablespaces with gbak -ts_map option
DESCRIPTION: 
    Not all specifying tablespaces exist.
    Expect no errors.
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_map_not_existing_ts.py
"""

import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()
act = python_act('db')

restored_db = db_factory(filename='restore.fdb', do_not_create=True)


@pytest.mark.version('>=6.0')
def test_1(act: Action, restored_db: Database, tmp_path: Path):

    ts_files = {}
    for i in range(1, 5):
        key = f'TS{i}'
        ts_files[key] = tmp_path / f'gbak_ts{i}.dat'

    script = f"""
    create tablespace TS1 FILE '{ts_files['TS1']}';
    create tablespace TS2 FILE '{ts_files['TS2']}';
    commit;

    create table TEST_TABLE1(ID INT UNIQUE, NAME VARCHAR(20) NOT NULL) IN TABLESPACE TS1;
    create table TEST_TABLE2(ID INT UNIQUE, NMB BIGINT, DESCRIPTION VARCHAR(100)) IN TABLESPACE TS2;
    commit;

    insert into TEST_TABLE1 values(1, 'One');
    insert into TEST_TABLE2 values(10, '1111', 'Ten and one digits');
    commit;
    """

    act.isql(switches=['-q'], input=script)

    test_db_backup = tmp_path / 'gbak_ts_backup.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    ts_map_file = Path(tmp_path / 'gbak_ts_map.txt')
    ts_map = ""
    for key in ts_files.keys():
        ts_line = f'{key} {ts_files[key]}'.replace('gbak_ts', 'gbak_ts_new')
        ts_map += ts_line+'\n'
    ts_map_file.write_text(ts_map)

    act.gbak(switches=['-R', test_db_backup, restored_db.dsn, '-ts_map', ts_map_file])
    assert act.clean_stdout == ""
