#coding:utf-8

"""
ID:          issue-5132
ISSUE:       5132
TITLE:       Grant update(c) on t to U01 with grant option: user U01 will not be able to `revoke update(c) on t from <user | role>` if this `U01` do some DML before revoke
DESCRIPTION:
JIRA:        CORE-4836
FBTEST:      bugs.core_4836
NOTES:
    [12.12.2023] pzotov
    Added 'SQLSTATE' in substitutions: runtime error must not be filtered out by '?!(...)' pattern
    ("negative lookahead assertion", see https://docs.python.org/3/library/re.html#regular-expression-syntax).
    Added 'combine_output = True' in order to see SQLSTATE if any error occurs.
"""

import pytest
from firebird.qa import *

db = db_factory()

tmp_user = user_factory('db', name='tmp$c4836', password='123', admin=True)
tmp_role = role_factory('db', name='tmp$r4836')

test_script = """
    recreate table test(id int, text varchar(30));

    grant select on test to public;
    grant update(text) on test to tmp$c4836 with grant option;
    commit;

    connect '$(DSN)' user tmp$c4836 password '123';

    grant update (text) on test to tmp$r4836;
    commit;
    show grants;
    commit;

    select * from test; -- this DML prevented to do subsequent `revoke update(text) on test from role` on build 3.0.0.31873

    commit;

    revoke update(text) on test from role tmp$r4836;
    commit;

    show grants;
    commit;
"""

act = isql_act('db', test_script, substitutions=[('^((?!SQLSTATE|C4836|R4836).)*$', '')])

expected_stdout = """
    GRANT UPDATE (TEXT) ON TEST TO USER TMP$C4836 WITH GRANT OPTION
    GRANT UPDATE (TEXT) ON TEST TO ROLE TMP$R4836 GRANTED BY TMP$C4836
    GRANT UPDATE (TEXT) ON TEST TO USER TMP$C4836 WITH GRANT OPTION
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_user: User, tmp_role: Role):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

