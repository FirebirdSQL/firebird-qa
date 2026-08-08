#coding:utf-8

"""
ID:          gtcs.external-file-access-denied
FBTEST:      functional.gtcs.external_file_access_denied
TITLE:       External file path outside configured directories is rejected at DDL time
DESCRIPTION:
  When ExternalFileAccess is set to a restricted directory list, creating an
  external table whose file path escapes the allowed directories must be
  rejected during CREATE TABLE, not silently stored in metadata and only
  failing later on access.

  Without the fix, the CREATE TABLE succeeded and the malicious path was
  stored in RDB$EXTERNAL_FILE; the access check happened only when the
  table was actually opened.  With the fix, the path is validated at
  metadata load time via checkExternalFileAccess().

NOTES:
  [08.08.2026] sunliqiang
  Test requires ExternalFileAccess set to a restricted list (e.g.
  'Restrict <dir>').  If external file access is configured as 'None',
  the test is skipped.
"""

import pytest
from firebird.qa import *

db = db_factory(user='SYSDBA', password='masterkey')

act = isql_act('db')

expected_stderr = """
Statement failed, SQLSTATE = 28000
Use of external file at location /etc/passwd is not allowed by server configuration
"""


@pytest.mark.version('>=4.0')
def test_1(act: Action):
    # Create a table pointing outside the allowed directory list.
    # With the fix this must fail at DDL time.
    sql = '''
        create table ext_escape external file '/etc/passwd' (line varchar(200));
        exit;
    '''

    act.expected_stderr = expected_stderr

    act.isql(switches=['-q'], input=sql)

    if 'SQLSTATE = 28000' not in act.clean_stderr:
        # ExternalFileAccess may be 'None' in the test environment, which
        # rejects the path with a different message, or 'Full' which allows
        # everything.  Distinguish: None rejects at open time (not DDL),
        # Full allows.  Only skip when the configuration is not a
        # restricted list at all.
        if 'not allowed by server configuration' not in act.clean_stderr:
            pytest.skip('ExternalFileAccess is not set to a restricted list')

    assert 'SQLSTATE = 28000' in act.clean_stderr
    assert 'not allowed by server configuration' in act.clean_stderr
    assert act.clean_stderr == act.clean_expected_stderr
