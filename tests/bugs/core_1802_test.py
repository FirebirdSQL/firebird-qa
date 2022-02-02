#coding:utf-8

"""
ID:          issue-873
ISSUE:       873
TITLE:       Maximum key size using PXW_CSY collation
DESCRIPTION:
JIRA:        CORE-1802
FBTEST:      bugs.core_1802
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE TAB21(
  ID INTEGER,
  A VARCHAR(490) CHARACTER SET WIN1250 COLLATE PXW_CSY,
  CONSTRAINT CU UNIQUE(A) );
COMMIT;
SHOW INDEX CU;
"""

act = isql_act('db', test_script)

expected_stdout = """CU UNIQUE INDEX ON TAB21(A)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

