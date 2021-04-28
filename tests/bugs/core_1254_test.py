#coding:utf-8
#
# id:           bugs.core_1254
# title:        Problem with DISTINCT and insensitive collations
# decription:   
# tracker_id:   CORE-1254
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST
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

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT GROUP_ID, QUESTION, SUM(SCORE) FROM TEST GROUP BY 1,2;
SELECT DISTINCT GROUP_ID, QUESTION FROM TEST;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

