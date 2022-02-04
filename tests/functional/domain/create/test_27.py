#coding:utf-8

"""
ID:          domain.create-27
FBTEST:      functional.domain.create.27
TITLE:       CREATE DOMAIN - BLOB SUB TYPE
DESCRIPTION: Domain creation based on BLOB datatype with SUBTYPE specification
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test BLOB SUB_TYPE 1;
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            BLOB segment 80, subtype TEXT Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
