#coding:utf-8
#
# id:           functional.exception.drop.03
# title:        DROP EXCEPTION - that doesn't exists
# decription:   DROP EXCEPTION - that doesn't exists
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.exception.drop.drop_exception_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP EXCEPTION test;
SHOW EXCEPTION test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP EXCEPTION TEST failed
-Exception not found
There is no exception TEST in this database

"""

@pytest.mark.version('>=3.0')
def test_03_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

