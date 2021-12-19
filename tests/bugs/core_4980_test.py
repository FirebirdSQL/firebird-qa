#coding:utf-8
#
# id:           bugs.core_4980
# title:        Operator REVOKE can modify rights granted to system tables at DB creation time
# decription:
#                    We create here NON-privileged user and revoke any right from him. Also create trivial table TEST.
#                    Then try to connect with as user and query non-system table TEST and system tables.
#                    Query to table TEST should be denied, but queries to RDB-tables should run OK and display their data.
#
# tracker_id:   CORE-4980
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP_C4980
    WHO_AM_I                        TMP_C4980
    RDB$CHARACTER_SET_NAME          NONE
    WHO_AM_I                        TMP_C4980
    RDB$RELATION_NAME               RDB$PAGES
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
"""

user_1 = user_factory('db_1', name='tmp_c4980', password='123')

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action, user_1: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set wng off;

    recreate table test(id int);
    commit;
    insert into test values(1);
    commit;

    connect '$(DSN)' user tmp_c4980 password '123';

    set list on;
    select current_user as who_am_i from rdb$database;
    select current_user as who_am_i, r.rdb$character_set_name from rdb$database r;
    select current_user as who_am_i, r.rdb$relation_name from rdb$relations r order by rdb$relation_id rows 1;
    select current_user as who_am_i, t.id from test t; -- this should ALWAYS fail because this is non-system table.
    commit;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    WHO_AM_I                        TMP_C4980
    WHO_AM_I                        TMP_C4980
    RDB$CHARACTER_SET_NAME          NONE
    WHO_AM_I                        TMP_C4980
    RDB$RELATION_NAME               RDB$PAGES
"""

expected_stderr_2 = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP_C4980
"""

user_2 = user_factory('db_2', name='tmp_c4980', password='123')

@pytest.mark.version('>=4.0')
def test_2(act_2: Action, user_2: User):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr
    assert act_2.clean_expected_stdout == act_2.clean_stdout

