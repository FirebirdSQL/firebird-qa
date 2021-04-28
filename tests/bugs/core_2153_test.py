#coding:utf-8
#
# id:           bugs.core_2153
# title:        SIMILAR TO predicate hangs with "|" option
# decription:   
# tracker_id:   CORE-2153
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select iif( 'avieieavav' similar to '%(av|ie){2,}%', 1, 0) r from rdb$database;
    select iif( 'avieieieav' similar to '%((av)|(ie)){2,}%', 1, 0) r from rdb$database;
    select iif( 'eiavieieav' similar to '%(av)|{2,}%', 1, 0) r from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    R                               1
    R                               1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Invalid SIMILAR TO pattern
  """

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

