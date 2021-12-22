#coding:utf-8
#
# id:           functional.database.create.11
# title:        CREATE DATABASE - Default char set NONE
# decription:   This test should be implemented for all char sets.
# tracker_id:   
# min_versions: []
# versions:     2.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT RDB$CHARACTER_SET_NAME FROM rdb$Database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$CHARACTER_SET_NAME
    NONE
"""

@pytest.mark.version('>=2.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

