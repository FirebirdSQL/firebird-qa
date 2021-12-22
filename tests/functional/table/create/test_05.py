#coding:utf-8
#
# id:           functional.table.create.05
# title:        CREATE TABLE - create table with same name
# decription:   CREATE TABLE - create table with same name
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.table.create.create_table_05

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test(
 c1 SMALLINT
);
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE test(
 c1 SMALLINT,
 c2 INTEGER
);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42S01
unsuccessful metadata update
-CREATE TABLE TEST failed
-Table TEST already exists
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

