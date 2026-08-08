#coding:utf-8

"""
ID:          gtcs.external-file-allowed-dir
FBTEST:      functional.gtcs.external_file_allowed_dir
TITLE:       External table in the allowed directory still works
DESCRIPTION:
  Regression test for the external file path validation added at metadata
  load time.  A table pointing to a file inside the configured allowed
  directory must still be usable.

NOTES:
  [08.08.2026] sunliqiang
  Test requires ExternalFileAccess set to a restricted list that includes
  the test temp directory (e.g. 'Restrict /tmp').  Skipped otherwise.
"""

from pathlib import Path
import pytest
from firebird.qa import *

db = db_factory(user='SYSDBA', password='masterkey')

act = isql_act('db')

tmp_ext_file = temp_file('ext_allowed_dir_test.dat')

expected_stdout = """
ID                              42
"""


@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_ext_file: Path):
    sql = f'''
        create table ext_ok external file '{tmp_ext_file}' (id int);
        commit;
        insert into ext_ok (id) values (42);
        commit;
        set list on;
        select id from ext_ok;
        exit;
    '''

    act.isql(switches=['-q'], input=sql)

    if 'not allowed by server configuration' in act.clean_stderr:
        pytest.skip('ExternalFileAccess does not include the temp directory')

    act.expected_stdout = expected_stdout
    act.expected_stderr = ""

    assert act.clean_stdout == act.clean_expected_stdout
    assert act.clean_stderr == ""
