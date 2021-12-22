#coding:utf-8
#
# id:           bugs.core_0871
# title:        Incorrect handling of null within view - returns 0
# decription:   
# tracker_id:   CORE-871
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_871

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN D INTEGER NOT NULL;
CREATE TABLE T (A D);
CREATE TABLE U (B D);
CREATE VIEW V (A, B) AS
SELECT T.A, U.B FROM T LEFT JOIN U ON (T.A = U.B);

COMMIT;

INSERT INTO T VALUES(1);
COMMIT;

"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT * FROM V;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """A            B
============ ============
           1       <null>

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

