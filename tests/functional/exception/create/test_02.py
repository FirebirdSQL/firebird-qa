#coding:utf-8
#
# id:           functional.exception.create.02
# title:        CREATE EXCEPTION - try create Exception with the same name
# decription:   CREATE EXCEPTION - try create Exception with the same name
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE EXCEPTION
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.exception.create.create_exception_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE EXCEPTION test 'A1';
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE EXCEPTION test 'message to show';"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE EXCEPTION TEST failed
-Exception TEST already exists

"""

@pytest.mark.version('>=3.0')
def test_02_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

