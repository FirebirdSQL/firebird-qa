#coding:utf-8

"""
ID:          domain.create-32
FBTEST:      functional.domain.create.32
TITLE:       CREATE DOMAIN - DEFAULT literal
DESCRIPTION: Domain creation based on VARCHAR datatype with literal DEFAULT specification
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test VARCHAR(32) DEFAULT 'def_value';
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(32) Nullable
DEFAULT 'def_value'"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
