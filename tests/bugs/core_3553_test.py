#coding:utf-8

"""
ID:          issue-3909
ISSUE:       3909
TITLE:       Nested loop plan is chosen instead of the sort merge for joining independent
  streams using keys of different types
DESCRIPTION:
JIRA:        CORE-3553
FBTEST:      bugs.core_3553
NOTES:
    [07.04.2022] pzotov
    FB 5.0.0.455 and later: data sources with equal cardinality now present in the HASH plan in order they are specified in the query.
    Reversed order was used before this build. Because of this, two cases of expected stdout must be taken in account, see variables
    'fb3x_checked_stdout' and 'fb5x_checked_stdout'.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set planonly;
    select count(*)
    from rdb$database d1
    join rdb$database d2  on cast(d1.rdb$relation_id as char(10)) = cast(d2.rdb$relation_id as char(20));
"""

act = isql_act('db', test_script)

fb3x_checked_stdout = """
    PLAN HASH (D2 NATURAL, D1 NATURAL)
"""

fb5x_checked_stdout = """
    PLAN HASH (D1 NATURAL, D2 NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    with act.connect_server() as srv:
        engine_major = int(srv.info.engine_version)

    act.expected_stdout = fb3x_checked_stdout if engine_major < 5 else fb5x_checked_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

