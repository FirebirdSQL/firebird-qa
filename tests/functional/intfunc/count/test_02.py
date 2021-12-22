#coding:utf-8
#
# id:           functional.intfunc.count.02
# title:        COUNT
# decription:   Count of Not Null values and count of rows and count of distinct values
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.intfunc.count.count_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER);
INSERT INTO test VALUES(0);
INSERT INTO test VALUES(0);
INSERT INTO test VALUES(null);
INSERT INTO test VALUES(null);
INSERT INTO test VALUES(null);
INSERT INTO test VALUES(1);
INSERT INTO test VALUES(1);
INSERT INTO test VALUES(1);
INSERT INTO test VALUES(1);
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT COUNT(*), COUNT(ID), COUNT(DISTINCT ID) FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                COUNT                 COUNT                 COUNT
===================== ===================== =====================
                    9                     6                     2
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

