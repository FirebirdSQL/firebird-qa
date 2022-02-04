#coding:utf-8

"""
ID:          domain.drop-02
FBTEST:      functional.domain.drop.02
TITLE:       DROP DOMAIN - in use
DESCRIPTION:
"""

import pytest
from firebird.qa import *

init_script = """CREATE DOMAIN test SMALLINT;
CREATE TABLE tb( id test);"""

db = db_factory(init=init_script)

act = isql_act('db', "DROP DOMAIN test;")

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP DOMAIN TEST failed
-Domain TEST is used in table TB (local name ID) and cannot be dropped
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
