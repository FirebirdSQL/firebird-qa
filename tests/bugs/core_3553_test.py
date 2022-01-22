#coding:utf-8

"""
ID:          issue-3909
ISSUE:       3909
TITLE:       Nested loop plan is chosen instead of the sort merge for joining independent streams using keys of different types
DESCRIPTION:
JIRA:        CORE-3553
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """SET PLAN ON;
select count(*)
from rdb$database d1 join rdb$database d2
  on cast(d1.rdb$relation_id as char(10)) = cast(d2.rdb$relation_id as char(20));
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN HASH (D2 NATURAL, D1 NATURAL)

                COUNT
=====================
                    1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

