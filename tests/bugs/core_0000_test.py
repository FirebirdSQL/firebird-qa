#coding:utf-8

"""
ID:          dummy
TITLE:       Dummy test
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t1(id int);
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    try:
        act.execute()
    except ExecutionError as e:
        pytest.fail("Test script execution failed", pytrace=False)


