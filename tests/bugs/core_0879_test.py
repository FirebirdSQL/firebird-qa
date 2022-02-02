#coding:utf-8

"""
ID:          issue-1272
ISSUE:       1272
TITLE:       Dependencies are not cleared when creation of expression index fails
DESCRIPTION:
JIRA:        CORE-879
FBTEST:      bugs.core_0879
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table tab ( a varchar(10000) );
    commit;
    create index ix on tab computed by (upper(a));
    drop table tab;
    commit;
    show table tab;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -key size exceeds implementation restriction for index "IX"
    There is no table TAB in this database
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

