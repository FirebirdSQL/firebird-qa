#coding:utf-8

"""
ID:          issue-828
ISSUE:       828
TITLE:       Foreign key relation VARCHAR <-> INT
DESCRIPTION:
JIRA:        CORE-480
"""

import pytest
from firebird.qa import *

init_script = """create table T1 (PK1 INTEGER, COL VARCHAR(10));
commit;"""

db = db_factory(init=init_script)

test_script = """create table T2 (PK2 INTEGER, FK1 VARCHAR(10), COL VARCHAR(10),
foreign key (FK1) references T1 (PK1));

"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE T2 failed
-could not find UNIQUE or PRIMARY KEY constraint in table T1 with specified columns
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

