#coding:utf-8

"""
ID:          gtcs.external-file-allowed-dir
FBTEST:      functional.gtcs.external_file_allowed_dir
TITLE:       External table in the allowed directory still works
DESCRIPTION:
  Regression test for external file path validation at metadata load time.

  When ExternalFileAccess is restricted to the directory containing the
  test database, an external table whose file is located inside that
  directory must still work normally.

NOTES:
  [08.08.2026] sunliqiang
  The test database uses a dedicated databases.conf alias with
  ExternalFileAccess restricted to its database directory.
"""

from pathlib import Path

import pytest
from firebird.qa import *


REQUIRED_ALIAS = 'tmp_external_file_allowed_alias'

db = db_factory(filename='#' + REQUIRED_ALIAS, user='SYSDBA', password='masterkey', async_write=False, do_not_drop=True)

act = isql_act('db')


expected_stdout = """
ID                              42
"""


@pytest.mark.version('>=4.0')
def test_1(act: Action):

    # The database itself is located in the directory configured in
    # ExternalFileAccess, so a sibling external file is guaranteed to
    # be inside the allowed directory.
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute('select mon$database_name from mon$database')
        db_path = Path(cur.fetchone()[0])

    ext_file = db_path.parent / 'ext_access_allowed_test.dat'

    # Remove leftovers from an interrupted/failed previous test run.
    ext_file.unlink(missing_ok=True)

    external_file = str(ext_file).replace("'", "''")

    sql = f"""
        create table ext_ok external file '{external_file}'
        (
            id int
        );
        commit;

        insert into ext_ok (id) values (42);
        commit;

        set list on;
        select id from ext_ok;

        drop table ext_ok;
        commit;

        exit;
    """

    act.expected_stdout = expected_stdout
    act.expected_stderr = ""

    try:
        act.isql(switches=['-q'], input=sql)

        assert act.clean_stdout == act.clean_expected_stdout
        assert act.clean_stderr == act.clean_expected_stderr
    finally:
        ext_file.unlink(missing_ok=True)
