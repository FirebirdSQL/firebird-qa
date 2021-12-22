#coding:utf-8
#
# id:           functional.index.create.11
# title:        CREATE UNIQUE INDEX - Non unique data in table
# decription:   CREATE UNIQUE INDEX - Non unique data in table
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               SHOW INDEX
# tracker_id:   
# min_versions: []
# versions:     2.5.3
# qmid:         functional.index.create.create_index_11

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE t( a INTEGER);
commit;
INSERT INTO t VALUES(0);
INSERT INTO t VALUES(0);
INSERT INTO t VALUES(1);
INSERT INTO t VALUES(2);
INSERT INTO t VALUES(3);
INSERT INTO t VALUES(4);
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE UNIQUE INDEX test ON t(a);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 23000
attempt to store duplicate value (visible to active transactions) in unique index "TEST"
-Problematic key value is ("A" = 0)"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

