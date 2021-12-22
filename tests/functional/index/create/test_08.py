#coding:utf-8
#
# id:           functional.index.create.08
# title:        CREATE INDEX - Table with data
# decription:   CREATE INDEX - Table with data
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               SHOW INDEX
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.index.create.create_index_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
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
INSERT INTO t VALUES(null);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE INDEX test ON t(a);
SHOW INDEX test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST INDEX ON T(A)"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

