#coding:utf-8
#
# id:           functional.intfunc.cast.12
# title:        CAST CHAR -> TIME
# decription:   CAST CHAR -> TIME
#               Be careful about date format on FB server !
#               Universal format is not defined or not documented.
#               
#               Dependencies:
#               CREATE DATABASE
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     2.5
# qmid:         functional.intfunc.cast.cast_12

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT CAST('9:11:60' AS TIME) FROM rdb$Database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """         CAST
============="""
expected_stderr_1 = '''Statement failed, SQLSTATE = 22018

conversion error from string "9:11:60"'''

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout

