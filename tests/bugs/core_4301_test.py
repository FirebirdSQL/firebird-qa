#coding:utf-8
#
# id:           bugs.core_4301
# title:        Non-ASCII data in SEC$USERS is not read correctly
# decription:
# tracker_id:   CORE-4301
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Note: this test differs from ticket: instead of add COMMENTS to users
    -- it only defines their `firstname` attribute, because sec$users.sec$description
    -- can be displayed only when plugin UserManager = Srp.
    -- Field `firstname` is defined as:
    -- VARCHAR(32) CHARACTER SET UNICODE_FSS COLLATE UNICODE_FSS
    -- we can put in it max 16 non-ascii characters
    create or alter user u30a password 'u30a' firstname 'Полиграф Шариков';
    create or alter user u30b password 'u30b' firstname 'Léopold Frédéric';
    commit;
    set list on;
    select u.sec$user_name, u.sec$first_name
    from sec$users u
    where upper(u.sec$user_name) in (upper('u30a'), upper('u30b'));
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SEC$USER_NAME                   U30A
    SEC$FIRST_NAME                  Полиграф Шариков
    SEC$USER_NAME                   U30B
    SEC$FIRST_NAME                  Léopold Frédéric
"""

# Note use of "do_not_create", as we want to create user in test script
# but we want to clean it up via fixture teardown
user_1a = user_factory('db_1', name='u30a', password='u30a', do_not_create=True)
user_1b = user_factory('db_1', name='u30b', password='u30b', do_not_create=True)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, user_1a: User, user_1b: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

