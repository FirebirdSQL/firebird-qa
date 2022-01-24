#coding:utf-8

"""
ID:          issue-5271
ISSUE:       5271
TITLE:       Operator REVOKE can modify rights granted to system tables at DB creation time
DESCRIPTION:
  We create here NON-privileged user and revoke any right from him. Also create trivial table TEST.
  Then try to connect with as user and query non-system table TEST and system tables.
  Query to table TEST should be denied, but queries to RDB-tables should run OK and display their data.
JIRA:        CORE-4980
"""

import pytest
from firebird.qa import *

db = db_factory()

tmp_user = user_factory('db', name='tmp_c4980', password='123')

test_script = """
    set wng off;

    recreate table test(id int);
    commit;
    insert into test values(1);
    commit;

    connect '$(DSN)' user tmp_c4980 password '123';

    -- All subsequent statements (being issued by TMP_C4980) failed on 3.0.0.32134 and runs OK on build 32136:
    set list on;

    select current_user as who_am_i from rdb$database;
    select current_user as who_am_i, r.rdb$character_set_name from rdb$database r;
    select current_user as who_am_i, r.rdb$relation_name from rdb$relations r order by rdb$relation_id rows 1;
    select current_user as who_am_i, t.id from test t; -- this should ALWAYS fail because this is non-system table.
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    WHO_AM_I                        TMP_C4980
    WHO_AM_I                        TMP_C4980
    RDB$CHARACTER_SET_NAME          NONE
    WHO_AM_I                        TMP_C4980
    RDB$RELATION_NAME               RDB$PAGES
"""

# version: 3.0

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action, tmp_user: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_1
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

# version: 4.0

expected_stderr_2 = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP_C4980
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action, tmp_user: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr_2
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

