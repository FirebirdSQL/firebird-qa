#coding:utf-8

"""
ID:          issue-1479
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/1479
TITLE:       ALTER DOMAIN and ALTER TABLE don't allow to change character set and/or collation
DESCRIPTION:
JIRA:        CORE-1058
FBTEST:      bugs.core_1058
NOTES:
    [05.10.2023] pzotov
    Removed SHOW command for check result because its output often changes.
    It is enough for this test to verify just absense of any error messages.
"""

import pytest
from firebird.qa import *

db = db_factory(init=init_script)

test_script = """
    create domain dm_test varchar(10) character set win1251;
    create table test1(s dm_test);
    create table test2(s varchar(10) character set win1251);
    ---------
    alter domain dm_test varchar(10) character set utf8;
    alter domain dm_test varchar(10) character set utf8 collate unicode_ci;
"""

act = isql_act('db', test_script)

expected_stdout = """
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

