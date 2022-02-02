#coding:utf-8

"""
ID:          issue-4586
ISSUE:       4586
TITLE:       Context parsing error with derived tables and CASE functions
DESCRIPTION:
JIRA:        CORE-4262
FBTEST:      bugs.core_4262
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """set planonly;
select col as col1, col as col2
from (
    select case when exists (select 1 from rdb$database ) then 1 else 0 end as col
    from rdb$relations
);
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (RDB$DATABASE NATURAL)
PLAN (RDB$RELATIONS NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
