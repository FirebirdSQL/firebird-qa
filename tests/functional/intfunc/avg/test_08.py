#coding:utf-8
#
# id:           functional.intfunc.avg.08
# title:        AVG - NULL test
# decription:   Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               INSERT
#               SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.intfunc.avg.avg_08

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER);
INSERT INTO test VALUES(NULL);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT AVG(id) FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                  AVG
=====================

               <null>"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

