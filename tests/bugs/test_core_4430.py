#coding:utf-8
#
# id:           bugs.core_4430
# title:        Properties of user created in Legacy_UserManager padded with space up to 10 character
# decription:   
# tracker_id:   CORE-4430
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed padded output in WI-T3.0.0.30809 Firebird 3.0 Alpha 2:
    --    SEC$USER_NAME                   TMP$C4430
    --    FIRST_NAME_WITH_DOT             john                            .
    --    LAST_NAME_WITH_DOT              smith                           .

    create user tmp$c4430 password '123' firstname 'john' lastname 'smith';
    commit;
    set list on;
    select 
        sec$user_name, 
        sec$first_name || '.' first_name_with_dot, 
        sec$last_name  || '.' last_name_with_dot 
    from sec$users
    where sec$user_name = upper('tmp$c4430');
    drop user tmp$c4430;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SEC$USER_NAME                   TMP$C4430
    FIRST_NAME_WITH_DOT             john.
    LAST_NAME_WITH_DOT              smith.
  """

@pytest.mark.version('>=3.0')
def test_core_4430_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

