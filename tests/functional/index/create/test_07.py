#coding:utf-8
#
# id:           functional.index.create.07
# title:        CREATE INDEX - Multi column
# decription:   CREATE INDEX - Multi column
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               SHOW INDEX
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.index.create.create_index_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE t( a INTEGER, b INT, c INT, d INT);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE INDEX test ON t(a,b,c,d);
SHOW INDEX test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEST INDEX ON T(A, B, C, D)"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

