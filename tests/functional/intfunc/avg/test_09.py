#coding:utf-8
#
# id:           functional.intfunc.avg.09
# title:        AVG - DOUBLE PRECISION
# decription:   AVG from single DOUBLE PRECISION row
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.intfunc.avg.avg_09

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id DOUBLE PRECISION NOT NULL);
INSERT INTO test VALUES(5.123456789);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT AVG(id) FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                    AVG
=======================

5.123456789000000"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

