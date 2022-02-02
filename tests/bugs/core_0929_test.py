#coding:utf-8

"""
ID:          issue-1330
ISSUE:       1330
TITLE:       Bug in DSQL parameter
DESCRIPTION:
JIRA:        CORE-336
FBTEST:      bugs.core_0929
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE TEST (MYDATE DATE NOT NULL PRIMARY KEY);
COMMIT;

INSERT INTO TEST VALUES (CURRENT_DATE);
INSERT INTO TEST VALUES (CURRENT_DATE + 1);
INSERT INTO TEST VALUES (CURRENT_DATE + 2);
INSERT INTO TEST VALUES (CURRENT_DATE + 3);
COMMIT;

"""

db = db_factory(init=init_script)

act = python_act('db')

@pytest.mark.version('>=3')
def test_1(act: Action):
    with act.db.connect() as con:
        c = con.cursor()
        try:
            c.prepare('SELECT * FROM TEST WHERE MYDATE + CAST(? AS INTEGER) >= ?')
        except:
            pytest.fail("Test FAILED")


