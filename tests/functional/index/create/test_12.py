#coding:utf-8
#
# id:           functional.index.create.12
# title:        CREATE UNIQUE INDEX - Null value in table
# decription:   CREATE UNIQUE INDEX - Null value in table
#               
#               Note: Misinterpretable message (attempt to store duplicate value)
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               SHOW INDEX
# tracker_id:   
# min_versions: []
# versions:     1.5
# qmid:         functional.index.create.create_index_12

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE t( a INTEGER);
commit;
INSERT INTO t VALUES(null);
INSERT INTO t VALUES(0);
INSERT INTO t VALUES(1);
INSERT INTO t VALUES(2);
INSERT INTO t VALUES(3);
INSERT INTO t VALUES(4);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE UNIQUE INDEX test ON t(a);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=1.5')
def test_12_1(act_1: Action):
    act_1.execute()

