#coding:utf-8

"""
ID:          domain.create-18
FBTEST:      functional.domain.create.18
TITLE:       CREATE DOMAIN - VARCHAR
DESCRIPTION: Simple domain creation based VARCHAR datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test VARCHAR(32765);
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(32765) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
