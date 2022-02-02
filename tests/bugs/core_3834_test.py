#coding:utf-8

"""
ID:          issue-4176
ISSUE:       4176
TITLE:       Usage of a NATURAL JOIN with a derived table crashes the server
DESCRIPTION:
JIRA:        CORE-3834
FBTEST:      bugs.core_3834
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core3834.fbk')

test_script = """
    set planonly;
    select r.revision
    from ( select r.revision, r.stageid from tilemaps r ) r
    natural join logs g
    where stageid = ?
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN HASH (G NATURAL, R R NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

