#coding:utf-8

"""
ID:          utilites.gbak.tablespace.test_ts_mapping
TITLE:       Test restore of a database with tablespaces with gbak -ts_mapping option
DESCRIPTION: Check full syntax of ts_mapping instead ts_map option
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_mapping.py
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [
    ('/.*gbak_ts', 'gbak_ts'),
    ('.*\\.*gbak_ts', 'gbak_ts')
]

db = db_factory()
act = python_act('db', substitutions=substitutions)

restored_db = db_factory(filename='restore.fdb', do_not_create=True)

expected_stdout = """ 
RDB$TABLESPACE_NAME             TS
RDB$FILE_NAME                   gbak_ts_new.dat
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action, restored_db: Database, tmp_path: Path):
    
    ts_file = tmp_path / 'gbak_ts.dat'

    script=f"""
    create tablespace TS FILE '{ts_file}';
    commit;

    create table TEST_TABLE1(ID INT UNIQUE, NAME VARCHAR(20) NOT NULL) IN TABLESPACE TS;
    commit;
    """

    act.isql(switches=['-q'], input=script)

    test_db_backup = tmp_path / 'gbak_ts_backup.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    ts_map_file = Path(tmp_path / 'gbak_ts_map.txt')
    map_line = f'TS {ts_file}'.replace('gbak_ts','gbak_ts_new')
    ts_map_file.write_text(map_line)

    act.gbak(switches=['-R', test_db_backup, restored_db.dsn, '-ts_mapping', ts_map_file])

    check_script = """
    set list on;
    select RDB$TABLESPACE_NAME from RDB$RELATIONS where RDB$RELATION_NAME='TEST_TABLE1';

    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS';
    """

    act.reset()
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=check_script, use_db=restored_db)
    assert act.clean_stdout == act.clean_expected_stdout
