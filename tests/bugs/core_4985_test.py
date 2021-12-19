#coding:utf-8
#
# id:           bugs.core_4985
# title:        Non-privileged user can implicitly count records in a restricted table
# decription:
# tracker_id:   CORE-4985
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 7
    WHO_AM_I                        TMP$C4985
    Records affected: 1
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP$C4985

    Statement failed, SQLSTATE = 28000
    no permission for SELECT access to TABLE TEST
    -Effective user is TMP$C4985
"""

user_1 = user_factory('db_1', name='TMP$C4985', password='123')

@pytest.mark.version('>=4.0')
def test_1(act_1: Action, user_1: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

