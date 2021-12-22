#coding:utf-8
#
# id:           functional.intfunc.count.01
# title:        COUNT - empty
# decription:   COUNT - Select from empty table
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.intfunc.count.count_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER);"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT COUNT(*) FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                COUNT
=====================
                    0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

