#coding:utf-8

"""
ID:          issue-1813
ISSUE:       1813
TITLE:       Few problems with domains's check constraints
DESCRIPTION:
JIRA:        CORE-1395
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE TEST ( ID INTEGER );
CREATE DOMAIN TEST_DOMAIN AS INTEGER CHECK (EXISTS(SELECT * FROM TEST WHERE ID=VALUE));
"""

db = db_factory(init=init_script)

test_script = """DROP TABLE TEST;
COMMIT;

"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-cannot delete
-COLUMN TEST.ID
-there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

