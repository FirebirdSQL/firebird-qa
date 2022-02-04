#coding:utf-8

"""
ID:          domain.drop-03
FBTEST:      functional.domain.drop.03
TITLE:       DROP DOMAIN - that doesn't exists
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

act = isql_act('db', "DROP DOMAIN test;")

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP DOMAIN TEST failed
-Domain not found
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
