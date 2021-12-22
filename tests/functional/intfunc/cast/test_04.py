#coding:utf-8
#
# id:           functional.intfunc.cast.04
# title:        CAST Numeric -> Numeric (Round down)
# decription:   CAST Numeric -> Numeric
#               Round down
#               
#               Dependencies:
#               CREATE DATABASE
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.intfunc.cast.cast_04

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT CAST(1.24999 AS NUMERIC(2,1)) FROM rdb$Database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """   CAST
=======

1.2"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

