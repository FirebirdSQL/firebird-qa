#coding:utf-8

"""
ID:          issue-6825
ISSUE:       6825
TITLE:       Correct error message for DROP VIEW
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate view v1 as select 1 x from rdb$database;
    create or alter user tmp$gh_6825 password '123' using plugin Srp;
    commit;
    connect '$(DSN)' user tmp$gh_6825 password '123';
    drop view v1;
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$gh_6825 using plugin Srp;
    commit;
"""

act = isql_act('db', test_script, substitutions=[('(-)?Effective user is.*', '')])

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -DROP VIEW V1 failed
    -no permission for DROP access to VIEW V1
    -Effective user is TMP$GH_6825
"""

@pytest.mark.version('>=3.0.8')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
