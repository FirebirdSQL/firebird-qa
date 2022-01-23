#coding:utf-8

"""
ID:          issue-4624
ISSUE:       4624
TITLE:       Non-ASCII data in SEC$USERS is not read correctly
DESCRIPTION:
JIRA:        CORE-4301
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

# Note use of "do_not_create", as we want to create user in test script
# but we want to clean it up via fixture teardown
user_a = user_factory('db', name='u30a', password='u30a', do_not_create=True)
user_b = user_factory('db', name='u30b', password='u30b', do_not_create=True)

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    SEC$USER_NAME                   U30A
    SEC$FIRST_NAME                  Полиграф Шариков
    SEC$USER_NAME                   U30B
    SEC$FIRST_NAME                  Léopold Frédéric
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, user_a: User, user_b: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

