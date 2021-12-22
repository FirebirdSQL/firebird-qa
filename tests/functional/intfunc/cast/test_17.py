#coding:utf-8
#
# id:           functional.intfunc.cast.17
# title:        CAST DATE -> TIMESTAMP
# decription:   CAST DATE -> TIMESTAMP
#               Be careful about date/time format on FB server !
#               Universal format is not defined or not documented.
#               
#               Dependencies:
#               CREATE DATABASE
#               CAST CHAR -> DATE
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.intfunc.cast.cast_17

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT CAST(CAST('10.2.1973' AS DATE) AS TIMESTAMP) FROM rdb$Database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                     CAST
=========================

1973-02-10 00:00:00.0000"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

