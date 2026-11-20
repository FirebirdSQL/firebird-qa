# coding:utf-8

"""
ID:          utilites.gbak.tablespace.test_ts_only_filename
TITLE:       Test restore of a database with tablespaces with gbak -ts option with only file name
DESCRIPTION: Expect a ts file is created in the db directory.
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_specify_filename.py.
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [
    ('/.*gbak_ts_specify_filename', 'gbak_ts_specify_filename'),
    ('.*\\.*gbak_ts_specify_filename', 'gbak_ts_specify_filename')
]

db = db_factory()
act = python_act('db', substitutions=substitutions)

restored_db = db_factory(filename='restore.fdb', do_not_create=True)

expected_stdout = """ 
RDB$FILE_NAME                   gbak_ts_specify_filename.dat
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, restored_db: Database, tmp_path: Path):
    ts_orig_filename = 'gbak_ts_orig_filename.dat'
    ts_orig_path = tmp_path / ts_orig_filename

    ts_filename = 'gbak_ts_specify_filename.dat'
    ts_path = Path(tmp_path / ts_filename)
    print(ts_path)

    script = f"""
    create tablespace TS1 FILE '{ts_orig_path}';
    commit;
    """

    act.isql(switches=['-q'], input=script)

    test_db_backup = tmp_path / 'gbak_ts_specify_filename.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    act.gbak(switches=['-R', test_db_backup, restored_db.dsn, '-ts', 'TS1', ts_filename])

    check_script = """
    set list on;
    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS1';
    """

    act.reset()
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=check_script, use_db=restored_db)
    assert (act.clean_stdout == act.clean_expected_stdout) and ts_path.is_file()
