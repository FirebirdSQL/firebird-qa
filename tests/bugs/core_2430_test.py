#coding:utf-8

"""
ID:          issue-2846
ISSUE:       2846
TITLE:       Server adds "NOT" at the end of default value for the TIMESTAMP field
DESCRIPTION:
JIRA:        CORE-2430
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE T1 (
    F1 BIGINT NOT NULL,
    F2 BIGINT NOT NULL,
    F3 TIMESTAMP DEFAULT current_timestamp NOT NULL
);

ALTER TABLE T1 ADD CONSTRAINT PK_T1 PRIMARY KEY (F1, F2);

show table t1;
"""

act = isql_act('db', test_script)

expected_stdout = """F1                              BIGINT Not Null
F2                              BIGINT Not Null
F3                              TIMESTAMP Not Null DEFAULT current_timestamp
CONSTRAINT PK_T1:
  Primary key (F1, F2)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

