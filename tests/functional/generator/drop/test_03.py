#coding:utf-8

"""
ID:          generator.drop-03
FBTEST:      functional.generator.drop.03
TITLE:       DROP GENERATOR - generator does not exists
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

act = isql_act('db', "DROP GENERATOR test;")

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP SEQUENCE TEST failed
-generator TEST is not defined
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
