#coding:utf-8

"""
ID:          domain.create-29
FBTEST:      functional.domain.create.29
TITLE:       CREATE DOMAIN - BLOB SEGMENT SIZE
DESCRIPTION: Domain creation based on BLOB datatype with SEGMENT SIZE specification
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test BLOB SEGMENT SIZE 244;
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            BLOB segment 244, subtype BINARY Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
