#coding:utf-8

"""
ID:          table.create-05
TITLE:       CREATE TABLE - create table with same name
DESCRIPTION:
FBTEST:      functional.table.create.05
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE test(
 c1 SMALLINT
);
commit;
"""

db = db_factory(init=init_script)

test_script = """CREATE TABLE test(
 c1 SMALLINT,
 c2 INTEGER
);
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42S01
unsuccessful metadata update
-CREATE TABLE TEST failed
-Table TEST already exists
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
