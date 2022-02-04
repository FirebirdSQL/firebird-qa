#coding:utf-8

"""
ID:          domain.create-41
FBTEST:      functional.domain.create.41
TITLE:       CREATE DOMAIN - create two domain with same name
DESCRIPTION: The creation of already existing domain must fail (SQLCODE -607)
"""

import pytest
from firebird.qa import *

db = db_factory(init="CREATE DOMAIN test AS INTEGER;")

act = isql_act('db', "CREATE DOMAIN test AS VARCHAR(32);")

expected_stderr = """Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE DOMAIN TEST failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_2" on table "RDB$FIELDS"
-Problematic key value is ("RDB$FIELD_NAME" = 'TEST')"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
