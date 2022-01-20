#coding:utf-8

"""
ID:          issue-1804
ISSUE:       1804
TITLE:       Generated columns
DESCRIPTION:
JIRA:        CORE-1386
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """CREATE TABLE TAB1 (COL1 INTEGER, COL2 GENERATED ALWAYS AS (COL1 +1), COL3 INTEGER GENERATED ALWAYS AS (COL1 +1));
COMMIT;
SHOW TABLE TAB1;
INSERT INTO TAB1 (COL1) VALUES (1);
COMMIT;
SELECT * FROM TAB1;

"""

act = isql_act('db', test_script)

expected_stdout = """COL1                            INTEGER Nullable
COL2                            Computed by: (COL1 +1)
COL3                            Computed by: (COL1 +1)

        COL1                  COL2         COL3
============ ===================== ============
           1                     2            2

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

