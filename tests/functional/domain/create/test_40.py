#coding:utf-8

"""
ID:          domain.create-40
FBTEST:      functional.domain.create.40
TITLE:       CREATE DOMAIN - all options
DESCRIPTION: Domain creation based on VARCHAR datatype with all possible options
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test AS VARCHAR(32) CHARACTER SET DOS437 DEFAULT USER NOT NULL CHECK(VALUE LIKE 'ER%') COLLATE DB_ITA437;
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(32) CHARACTER SET DOS437 Not Null
                                DEFAULT USER
                                CHECK(VALUE LIKE 'ER%')
COLLATE DB_ITA437"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
