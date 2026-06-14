#coding:utf-8

"""
ID:          issue-4471
ISSUE:       4471
TITLE:       Error "context already in use (BLR error)" when preparing a query with UNION
DESCRIPTION:
JIRA:        CORE-4144
NOTES:
    [14.06.2026] pzotov
    Changed query to reproduce problem: on 6.x we have to avoid comparing of RDB$DATABASE.RDB$RELATION_ID
    with some concrete values because GENERATOR is used to store generated relation_id instead of this field,
    see #bb280120.

    Confirmed crash on 3.0.0.30499-6638a2e (check possible only using command prompt and ISQL; not in this QA).
    Bug has been fixed in #01a6f1a6 (Jul 22 08:29:01 2013 +0000).
    Checked on 3.0.0.30550-01a6f1a -- all fine.
    Checked on 6.0.0.2002; 5.0.5.1826; 4.0.8.3279; 3.0.14.33855.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set heading off;
    select n
    from
    (
        select 1 as n from rdb$database d
        UNION ALL
        select 2 as n from rdb$database d
    )
    UNION ALL
    select cast(3 as bigint) from rdb$database d;
"""

act = isql_act('db', test_script)

expected_stdout = """
    1
    2
    3
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

