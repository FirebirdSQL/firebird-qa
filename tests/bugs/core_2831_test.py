#coding:utf-8

"""
ID:          issue-3217
ISSUE:       3217
TITLE:       isql shouldn't display db and user name when extracting a script
DESCRIPTION:
JIRA:        CORE-2831
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('^((?!Database:|User:).)*$', '')])

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.isql(switches=['-x'])
    assert act.clean_stdout == act.clean_expected_stdout

