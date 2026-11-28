# coding:utf-8

"""
ID:          utilites.gbak.tablespace.test_ts_not_all_spec
TITLE:       Test restore of a database with tablespaces with gbak -ts option
DESCRIPTION: 
    Not all existing tablespaces are specifying.
    Expect an error.
NOTES:
    The test was moved from tests/functional/restore/test_gbak_ts_not_all_spec.py
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [
    ('/.*gbak_ts', 'gbak_ts'),
    ('.*\\.*gbak_ts', 'gbak_ts')]

db = db_factory()
act = python_act('db', substitutions=substitutions)

restored_db = db_factory(filename='restore.fdb', do_not_create=True)

expected_stderr = """
gbak: ERROR:path to tablespace TS2 is not specified (original path: "gbak_ts2.dat")
gbak: ERROR:path to tablespace TS4 is not specified (original path: "gbak_ts4.dat")
gbak:Exiting before completion due to errors
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, restored_db: Database, tmp_path: Path):

    ts_files = {}
    for i in range(1, 5):
        key = f'TS{i}'
        ts_files[key] = tmp_path / f'gbak_ts{i}.dat'

    script = f"""
    create tablespace TS1 FILE '{ts_files['TS1']}';
    create tablespace TS2 FILE '{ts_files['TS2']}';
    create tablespace TS3 FILE '{ts_files['TS3']}';
    create tablespace TS4 FILE '{ts_files['TS4']}';
    commit;
    """

    act.isql(switches=['-q'], input=script)

    test_db_backup = tmp_path / 'gbak_ts_backup.fbk'
    act.gbak(switches=['-BACKUP_DATABASE', act.db.dsn, test_db_backup])

    ts_options = []
    for key in ['TS1', 'TS3']:
        tmp_file = str(ts_files[key]).replace('gbak_ts', 'gbak_ts_new')
        ts_options.extend(['-ts', key, tmp_file])

    act.expected_stderr = expected_stderr
    act.gbak(switches=['-R', test_db_backup, restored_db.dsn, *ts_options])
    assert act.clean_stderr == act.clean_expected_stderr
