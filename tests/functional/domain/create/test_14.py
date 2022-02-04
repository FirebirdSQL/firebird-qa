#coding:utf-8

"""
ID:          domain.create-14
FBTEST:      functional.domain.create.14
TITLE:       CREATE DOMAIN - NUMERIC ARRAY
DESCRIPTION: Array domain creation based on NUMERIC datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test NUMERIC(18,18)[32768];
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            ARRAY OF [32768]
NUMERIC(18, 18) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
