#coding:utf-8

"""
ID:          issue-5135
ISSUE:       5135
TITLE:       SHOW GRANTS does not display info about exceptions which were granted to user
DESCRIPTION:
JIRA:        CORE-4839
"""

import pytest
from firebird.qa import *

db = db_factory()

test_user = user_factory('db', name='tmp$c4839', password='123')

test_script = """
    recreate exception exc_foo 'Houston we have a problem: next sequence value is @1';
    recreate sequence gen_bar start with 9223372036854775807 increment by 2147483647;
    commit;

    grant usage on exception exc_foo to tmp$c4839; -- this wasn`t shown before rev. 61822 (build 3.0.0.31881), 2015-06-14 11:35
    grant usage on sequence gen_bar to tmp$c4839;
    commit;
    show grants;
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    /* Grant permissions for this database */
    GRANT USAGE ON SEQUENCE GEN_BAR TO USER TMP$C4839
    GRANT USAGE ON EXCEPTION EXC_FOO TO USER TMP$C4839
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, test_user: User):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

