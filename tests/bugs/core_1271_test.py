#coding:utf-8

"""
ID:          issue-1692
ISSUE:       1692
TITLE:       Ceation of invalid procedures/triggers allowed
DESCRIPTION:
JIRA:        CORE-1271
FBTEST:      bugs.core_1271
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create procedure p returns (out int) as
    begin
        for
            select rdb$relation_id
            from rdb$relations
            plan (rdb$relations order rdb$index_1)
            order by rdb$description
            into :out
        do
            suspend;
    end
    ^
    commit^
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 2F000
    Error while parsing procedure P's BLR
    -index RDB$INDEX_1 cannot be used in the specified plan
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

