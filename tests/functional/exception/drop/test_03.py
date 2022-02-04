#coding:utf-8

"""
ID:          exception.drop-03
FBTEST:      functional.exception.drop.03
TITLE:       DROP EXCEPTION - that doesn't exists
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """DROP EXCEPTION test;
SHOW EXCEPTION test;"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP EXCEPTION TEST failed
-Exception not found
There is no exception TEST in this database
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
