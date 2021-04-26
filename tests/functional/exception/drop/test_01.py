#coding:utf-8
#
# id:           functional.exception.drop.01
# title:        DROP EXCEPTION
# decription:   DROP EXCEPTION
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE EXCEPTION
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.exception.drop.drop_exception_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE EXCEPTION test 'message to show';
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """DROP EXCEPTION test;
SHOW EXCEPTION test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """There is no exception TEST in this database"""

@pytest.mark.version('>=1.0')
def test_01_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

