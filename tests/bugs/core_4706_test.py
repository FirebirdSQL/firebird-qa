#coding:utf-8

"""
ID:          issue-5014
ISSUE:       5014
TITLE:       ISQL pads blob columns wrongly when the column alias has more than 17 characters
DESCRIPTION:
JIRA:        CORE-4706
FBTEST:      bugs.core_4706
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set blob all;
    select cast('a' as blob) a, 1, cast('a' as blob) x2345678901234567890, 2 from rdb$database;
"""

act = isql_act('db', test_script, substitutions=[('=.*', '')])

expected_stdout = """
                A     CONSTANT X2345678901234567890     CONSTANT
              0:2            1                  0:1            2
A:
a
X2345678901234567890:
a
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

