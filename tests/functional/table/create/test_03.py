#coding:utf-8
#
# id:           functional.table.create.03
# title:        CREATE TABLE - charset + colations + domain
# decription:   CREATE TABLE - charset + colations + domain
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE DOMAIN
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         functional.table.create.create_table_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN test VARCHAR(32765)[40000];
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE test(
 c1 VARCHAR(40) CHARACTER SET CYRL COLLATE CYRL,
 c2 VARCHAR(40) CHARACTER SET DOS437 COLLATE DB_DEU437,
 c3 BLOB SUB_TYPE TEXT CHARACTER SET DOS437,
 c4 test
);
SHOW TABLE test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """C1                              VARCHAR(40) CHARACTER SET CYRL Nullable
C2                              VARCHAR(40) CHARACTER SET DOS437 Nullable
                                 COLLATE DB_DEU437
C3                              BLOB segment 80, subtype TEXT CHARACTER SET DOS437 Nullable
C4                              (TEST) ARRAY OF [40000]
VARCHAR(32765) Nullable"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

