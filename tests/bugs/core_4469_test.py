#coding:utf-8
#
# id:           bugs.core_4469
# title:        Add field in SEC$USERS reflecting whether a user has RDB$ADMIN role in security database
# decription:
# tracker_id:   CORE-4469
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('Statement failed, SQLSTATE = HY000', ''), ('record not found for user:.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    drop user boss1;
    drop user boss2;
    commit;

    create user boss1 password '123' grant admin role;
    commit;
    select SEC$ADMIN is_admin_boss1 from sec$users where sec$user_name = upper('boss1');


    create user boss2 password '456';
    commit;
    select SEC$ADMIN is_admin_boss2a from sec$users where sec$user_name = upper('boss2');

    alter user boss2 grant admin role;
    commit;
    select SEC$ADMIN is_admin_boss2b from sec$users where sec$user_name = upper('boss2');

    alter user boss2 revoke admin role;
    commit;
    select SEC$ADMIN is_admin_boss2c from sec$users where sec$user_name = upper('boss2');

    drop user boss1;
    drop user boss2;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    IS_ADMIN_BOSS1                  <true>
    IS_ADMIN_BOSS2A                 <false>
    IS_ADMIN_BOSS2B                 <true>
    IS_ADMIN_BOSS2C                 <false>
"""

expected_stderr_1 = """
Statement failed, SQLSTATE = HY000
record not found for user: BOSS1
Statement failed, SQLSTATE = HY000
record not found for user: BOSS2
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

