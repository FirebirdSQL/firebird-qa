#coding:utf-8

"""
ID:          domain.create-17
FBTEST:      functional.domain.create.17
TITLE:       CREATE DOMAIN - CHARACTER VARYING
DESCRIPTION: Simple domain creation based CHARACTER VARYING datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test CHARACTER VARYING(1);
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            VARCHAR(1) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
