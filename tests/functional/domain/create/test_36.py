#coding:utf-8

"""
ID:          domain.create-36
FBTEST:      functional.domain.create.36
TITLE:       CREATE DOMAIN - DEFAULT CURRENT_ROLE
DESCRIPTION: Domain creation based on VARCHAR datatype with CURRENT_ROLE DEFAULT specification
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test VARCHAR(32) DEFAULT CURRENT_ROLE;
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(32) Nullable
DEFAULT CURRENT_ROLE"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
