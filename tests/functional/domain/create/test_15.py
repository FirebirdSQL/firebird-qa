#coding:utf-8

"""
ID:          domain.create-15
FBTEST:      functional.domain.create.15
TITLE:       CREATE DOMAIN - CHAR
DESCRIPTION: Simple domain creation based CHAR datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test CHAR(300);
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            CHAR(300) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
