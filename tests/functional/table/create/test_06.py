#coding:utf-8

"""
ID:          table.create-06
TITLE:       CREATE TABLE - two column with same name
DESCRIPTION:
FBTEST:      functional.table.create.06
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE test(
 c1 SMALLINT,
 c1 INTEGER
);
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 23000
unsuccessful metadata update
-CREATE TABLE TEST failed
-violation of PRIMARY or UNIQUE KEY constraint "RDB$INDEX_15" on table "RDB$RELATION_FIELDS"
-Problematic key value is ("RDB$FIELD_NAME" = 'C1', "RDB$RELATION_NAME" = 'TEST')
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
