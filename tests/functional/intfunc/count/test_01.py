#coding:utf-8

"""
ID:          intfunc.count-01
TITLE:       COUNT - Select from empty table
DESCRIPTION:
FBTEST:      functional.intfunc.count.01
"""

import pytest
from firebird.qa import *

db = db_factory(init="CREATE TABLE test( id INTEGER);")

act = isql_act('db', "SELECT COUNT(*) FROM test;")

expected_stdout = """
COUNT
=====================
                    0
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
