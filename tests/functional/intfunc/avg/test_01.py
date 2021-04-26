#coding:utf-8
#
# id:           functional.intfunc.avg.01
# title:        AVG from single integer row
# decription:   AVG from single integer row
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.intfunc.avg.avg_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL CONSTRAINT unq UNIQUE,
                   text VARCHAR(32));
INSERT INTO test VALUES(5,null);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT AVG(id) FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                  AVG
=====================

                    5"""

@pytest.mark.version('>=1.0')
def test_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

