#coding:utf-8

"""
ID:          issue-3099
ISSUE:       3099
TITLE:       Common table expression context could be used with parameters
DESCRIPTION:
JIRA:        CORE-2699
"""

import pytest
from firebird.qa import *

db_1 = db_factory()

test_script = """
    with x as (
        select 1 n from rdb$database
    )
    select * from x(10);
"""

act = isql_act('db_1', test_script, substitutions=[('-At line.*', '')])

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -204
    -Procedure unknown
    -X
    -At line 4, column 15
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

