#coding:utf-8

"""
ID:          domain.create-38
FBTEST:      functional.domain.create.38
TITLE:       CREATE DOMAIN - CHECK
DESCRIPTION: Domain creation based on VARCHAR datatype with CHECK specification
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test VARCHAR(32) CHECK(VALUE LIKE 'ER%');
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(32) Nullable
CHECK(VALUE LIKE 'ER%')"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
