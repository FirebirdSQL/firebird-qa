#coding:utf-8

"""
ID:          issue-1678
ISSUE:       1678
TITLE:       Problem with DISTINCT and insensitive collations
DESCRIPTION:
JIRA:        CORE-1254
FBTEST:      bugs.core_1254
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE TEST
(GROUP_ID VARCHAR(1) CHARACTER SET UTF8 COLLATE UNICODE_CI,
QUESTION INTEGER,
SCORE INTEGER);
COMMIT;
INSERT INTO TEST (GROUP_ID,QUESTION,SCORE) VALUES ('a',1,1);
INSERT INTO TEST (GROUP_ID,QUESTION,SCORE) VALUES ('a',2,1);
INSERT INTO TEST (GROUP_ID,QUESTION,SCORE) VALUES ('a',3,1);
INSERT INTO TEST (GROUP_ID,QUESTION,SCORE) VALUES ('A',1,1);
INSERT INTO TEST (GROUP_ID,QUESTION,SCORE) VALUES ('A',2,1);
INSERT INTO TEST (GROUP_ID,QUESTION,SCORE) VALUES ('A',3,1);
COMMIT;

"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """SELECT GROUP_ID, QUESTION, SUM(SCORE) FROM TEST GROUP BY 1,2;
SELECT DISTINCT GROUP_ID, QUESTION FROM TEST;"""

act = isql_act('db', test_script)

expected_stdout = """
GROUP_ID     QUESTION                   SUM
======== ============ =====================
a                   1                     2
a                   2                     2
a                   3                     2


GROUP_ID     QUESTION
======== ============
a                   1
a                   2
a                   3

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

