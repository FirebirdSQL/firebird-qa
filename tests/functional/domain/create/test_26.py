#coding:utf-8

"""
ID:          domain.create-26
FBTEST:      functional.domain.create.26
TITLE:       CREATE DOMAIN - BLOB
DESCRIPTION: Simple domain creation based BLOB datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test BLOB;
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            BLOB segment 80, subtype BINARY Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
