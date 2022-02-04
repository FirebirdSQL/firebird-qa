#coding:utf-8

"""
ID:          domain.create-11
FBTEST:      functional.domain.create.11
TITLE:       CREATE DOMAIN - DECIMAL
DESCRIPTION: Simple domain creation based DECIMAL datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test DECIMAL(18,4);
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            DECIMAL(18, 4) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
