#coding:utf-8

"""
ID:          issue-3479
ISSUE:       3479
TITLE:       Cannot alter the domain after migrating from older versions
DESCRIPTION:
JIRA:        CORE-3101
FBTEST:      bugs.core_3101
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core3101-ods11.fbk')

test_script = """
    show domain state;
    alter domain state set default 0;
    commit;
    show domain state;
"""

act = isql_act('db', test_script)

expected_stdout = """
    STATE                           SMALLINT Nullable
    STATE                           SMALLINT Nullable
                                    default 0
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

