#coding:utf-8

"""
ID:          issue-1726
ISSUE:       1726
TITLE:       Indices not used for views
DESCRIPTION:
JIRA:        CORE-1306
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE "TABLE" (ID INTEGER NOT NULL PRIMARY KEY);

COMMIT;

INSERT INTO "TABLE" (ID) VALUES (1);
INSERT INTO "TABLE" (ID) VALUES (2);
INSERT INTO "TABLE" (ID) VALUES (3);

COMMIT;

CREATE VIEW "VIEW" AS SELECT * FROM "TABLE";

commit;"""

db = db_factory(init=init_script)

test_script = """set plan on;

SELECT * FROM "TABLE" WHERE ID = 1
UNION ALL
SELECT * FROM "VIEW" WHERE ID = 1 ;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (TABLE INDEX (RDB$PRIMARY1), VIEW TABLE INDEX (RDB$PRIMARY1))

          ID
============
           1
           1

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

