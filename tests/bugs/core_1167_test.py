#coding:utf-8

"""
ID:          issue-1590
ISSUE:       1590
TITLE:       CHARACTER SET GBK is not installed
DESCRIPTION:
  Default character set is GBK
  Create Table T1(ID integer, FName Varchar(20); -- OK
  Commit; ---Error Message: CHARACTER SET GBK is not installed
JIRA:        CORE-1167
"""

import pytest
from firebird.qa import *

db = db_factory(charset='GBK')

test_script = """Create Table T1(ID integer, FName Varchar(20) CHARACTER SET GBK);
COMMIT;
SHOW TABLE T1;
"""

act = isql_act('db', test_script)

expected_stdout = """ID                              INTEGER Nullable
FNAME                           VARCHAR(20) Nullable
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

