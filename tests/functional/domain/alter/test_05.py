#coding:utf-8

"""
ID:          domain.alter-05
FBTEST:      functional.domain.alter.05
TITLE:       ALTER DOMAIN - Alter domain that doesn't exists
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory(init="CREATE DOMAIN test VARCHAR(63);")

act = isql_act('db', "ALTER DOMAIN notexists DROP CONSTRAINT;")

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER DOMAIN NOTEXISTS failed
-Domain not found
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
