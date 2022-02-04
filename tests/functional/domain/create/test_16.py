#coding:utf-8

"""
ID:          domain.create-16
FBTEST:      functional.domain.create.16
TITLE:       CREATE DOMAIN - CHARACTER
DESCRIPTION: Simple domain creation based CHARACTER datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE DOMAIN test CHARACTER(32767);
SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            CHAR(32767) Nullable"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
