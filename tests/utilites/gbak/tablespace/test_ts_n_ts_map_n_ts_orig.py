# coding:utf-8

"""
ID:          utilites.gbak.tablespace.test_ts_n_ts_map_n_ts_orig
TITLE:       Test restore of a database with tablespaces with gbak options -ts_orig, -ts and -ts_map together
DESCRIPTION: Check that -ts_orig option does not replace paths specified by -ts and -ts_map options
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_ts_map_ts_origin.py.
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [('/.*gbak_ts', 'gbak_ts'), ('.*\\.*gbak_ts', 'gbak_ts')]

db = db_factory()
act = python_act('db', substitutions=substitutions)

restored_db = db_factory(filename='restore.fdb', do_not_create=True)

expected_stdout = """
RDB$TABLESPACE_NAME             TS1
RDB$TABLESPACE_NAME             TS2
RDB$TABLESPACE_NAME             PRIMARY

RDB$TABLESPACE_NAME             TS3
RDB$TABLESPACE_NAME             TS2
RDB$TABLESPACE_NAME             TS4

RDB$FILE_NAME                   gbak_ts_diff1.dat
RDB$FILE_NAME                   gbak_ts_diff2.dat
RDB$FILE_NAME                   gbak_ts_new3.dat
RDB$FILE_NAME                   gbak_ts_new4.dat
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, restored_db: Database, tmp_path: Path):

    ts_files = {}
    for i in range(1, 5):
        key = f'TS{i}'
        ts_files[key] = Path(tmp_path / f'gbak_ts{i}.dat')

    script = f"""
    create tablespace TS1 FILE '{ts_files['TS1']}';
    create tablespace TS2 FILE '{ts_files['TS2']}';
    create tablespace TS3 FILE '{ts_files['TS3']}';
    create tablespace TS4 FILE '{ts_files['TS4']}';
    commit;

    create table TEST_TABLE1(ID INT UNIQUE, NAME VARCHAR(20) NOT NULL) IN TABLESPACE TS1;
    create table TEST_TABLE2(ID INT UNIQUE, NMB BIGINT, DESCRIPTION VARCHAR(100)) IN TABLESPACE TS2;
    create table TEST_TABLE3(ID INT UNIQUE, PRICE NUMERIC(10,2), LINK VARCHAR(100));
    commit;

    create index IND_TS1 ON TEST_TABLE1(ID) IN TABLESPACE TS3;
    create index IND_TS2 ON TEST_TABLE2(ID, NMB);
    create index IND_TS3 ON TEST_TABLE3(PRICE, LINK) IN TABLESPACE TS4;
    commit;
    """
    act.isql(switches=['-q'], input=script)

    test_db_backup = tmp_path / 'gbak_ts_backup.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    for value in ts_files.values():
        if value.is_file():
            value.unlink()

    ts_map_file = Path(tmp_path / 'gbak_ts_map.txt')

    ts_options = ['-ts_map', ts_map_file]

    ts_map = ""
    for key in ts_files.keys():
        ts_line = f'{key} {ts_files[key]}'.replace('gbak_ts', 'gbak_ts_new')
        ts_map += ts_line+'\n'
        if (key == 'TS1') or (key == 'TS2'):
            diff_path = str(ts_files[key]).replace('gbak_ts', 'gbak_ts_diff')
            ts_options.extend(['-ts', key, diff_path])
    ts_map_file.write_text(ts_map)

    act.gbak(switches=['-R', test_db_backup, restored_db.dsn, *ts_options, '-ts_orig'])

    check_script = """
    set list on;
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE1';
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE2';
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE3';

    select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IND_TS1';
    select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IND_TS2';
    select RDB$TABLESPACE_NAME from RDB$INDICES where RDB$INDEX_NAME='IND_TS3';

    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS1';
    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS2';
    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS3';
    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS4';
    """

    act.reset()
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=check_script, use_db=restored_db)
    assert act.clean_stdout == act.clean_expected_stdout
