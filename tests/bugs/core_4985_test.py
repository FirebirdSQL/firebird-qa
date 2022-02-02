#coding:utf-8

"""
ID:          issue-5276
ISSUE:       5276
TITLE:       Non-privileged user can implicitly count records in a restricted table
DESCRIPTION:
JIRA:        CORE-4985
FBTEST:      bugs.core_4985
"""

import pytest
from firebird.qa import *

db = db_factory()

tmp_user = user_factory('db', name='TMP$C4985', password='123')

test_script = """
    -- Checked on build  of 24.03.2016 4.0 Unstable.

    set wng off;
    create table test(id int);
    set count on;
    insert into test select 1 from rdb$types rows 7;
    commit;
    revoke all on all from TMP$C4985;
    commit;

    connect '$(DSN)' user 'TMP$C4985' password '123';

    set list on;
    select current_user as who_am_i from rdb$database;
    select count(*) from test;
    set count on;
    select 1 from test;

    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Records affected: 7
    WHO_AM_I                        TMP$C4985
    Records affected: 1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP$C4985

    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP$C4985
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_user: User):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

