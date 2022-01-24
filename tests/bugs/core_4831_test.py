#coding:utf-8

"""
ID:          issue-5128
ISSUE:       5128
TITLE:       Revoke all on all from role <R> -- failed with "SQL role <R> does not exist in security database"
DESCRIPTION:
JIRA:        CORE-4831
"""

import pytest
from firebird.qa import *

db = db_factory()

role = role_factory('db', name='r_20150608_20h03m')

test_script = """
    set wng off;
    -- create role r_20150608_20h03m;
    -- commit;
    revoke all on all from role r_20150608_20h03m; -- this was failed, possibly due to: http://sourceforge.net/p/firebird/code/61729
    commit;
    show grants;
    -- commit;
    -- drop role r_20150608_20h03m;
    --commit;
"""

act = isql_act('db', test_script)

expected_stderr = """
There is no privilege granted in this database
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, role: Role):
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stdout == act.clean_expected_stdout and
            act.clean_stderr == act.clean_expected_stderr)
