#coding:utf-8
#
# id:           functional.generator.create_02
# title:        CREATE GENERATOR - try create gen with same name
# decription:   CREATE GENERATOR - try create gen with same name
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE GENERATOR
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.generator.create.create_generator_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    CREATE GENERATOR test;
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    CREATE GENERATOR test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE SEQUENCE TEST failed
    -Sequence TEST already exists
  """

@pytest.mark.version('>=3.0')
def test_create_02_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

