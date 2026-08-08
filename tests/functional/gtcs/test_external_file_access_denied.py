#coding:utf-8

"""
ID:          gtcs.external-file-access-denied
FBTEST:      functional.gtcs.external_file_access_denied
TITLE:       External file path outside configured directories is rejected at DDL time
DESCRIPTION:
  When ExternalFileAccess is restricted, creating an external table whose
  file path is outside the allowed directory must be rejected during
  CREATE TABLE.

  Without the fix, CREATE TABLE succeeds and the invalid path is stored
  in RDB$EXTERNAL_FILE. The access check is performed only when the
  external file is opened.

  With the fix, the path is validated while relation metadata is loaded,
  so CREATE TABLE fails immediately.

NOTES:
  [08.08.2026] sunliqiang
  The test database uses a dedicated databases.conf alias with
  ExternalFileAccess restricted to its database directory.
"""

from pathlib import Path

import pytest
from firebird.qa import *


REQUIRED_ALIAS = 'tmp_external_file_access_denied_alias'

db = db_factory(filename='#' + REQUIRED_ALIAS)

act = isql_act('db')


@pytest.mark.version('>=4.0')
def test_1(act: Action):

    # Obtain the physical database location. The database is created inside
    # the directory allowed by ExternalFileAccess.
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute('select mon$database_name from mon$database')
        db_path = Path(cur.fetchone()[0])

    allowed_dir = db_path.parent

    # Use a file in the parent directory, which is deliberately outside
    # ExternalFileAccess = Restrict <allowed_dir>.
    denied_file = allowed_dir.parent / 'ext_access_denied_test.dat'

    external_file = str(denied_file).replace("'", "''")

    sql = f"""
        create table ext_escape external file '{external_file}'
        (
            line varchar(200)
        );
        exit;
    """

    act.expected_stderr = f"""
Statement failed, SQLSTATE = 28000
Use of external file at location {denied_file} is not allowed by server configuration
"""

    act.isql(switches=['-q'], input=sql)

    assert act.clean_stderr == act.clean_expected_stderr
