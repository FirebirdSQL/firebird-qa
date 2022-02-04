#coding:utf-8

"""
ID:          domain.create-37
FBTEST:      functional.domain.create.37
TITLE:       CREATE DOMAIN - NOT NULL
DESCRIPTION: Domain creation based on VARCHAR datatype with NOT NULL specification
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test VARCHAR(32) NOT NULL;
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(32) Not Null"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
