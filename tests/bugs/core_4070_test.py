#coding:utf-8

"""
ID:          issue-4398
ISSUE:       4398
TITLE:       NOT-NULL-column can be used as primary key and filled with NULL-values
DESCRIPTION:
JIRA:        CORE-4070
FBTEST:      bugs.core_4070
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test01(uid char(16) character set octets collate octets);
    alter table test01 add constraint test01_pk primary key (uid);
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST01 failed
    -Column: UID not defined as NOT NULL - cannot be used in PRIMARY KEY constraint definition
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

