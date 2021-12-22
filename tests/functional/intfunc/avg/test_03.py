#coding:utf-8
#
# id:           functional.intfunc.avg.03
# title:        AVG - Test for INTEGER
# decription:   Round down (16/3 = 5.3)
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.intfunc.avg.avg_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL);
INSERT INTO test VALUES(5);
INSERT INTO test VALUES(5);
INSERT INTO test VALUES(6);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT AVG(id) FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                  AVG
=====================

5"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

