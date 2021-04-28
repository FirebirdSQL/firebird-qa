#coding:utf-8
#
# id:           bugs.core_2140
# title:        Error messages after parameters substitution contains '
#               ' characters instead of line break
# decription:   
# tracker_id:   CORE-2140
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = [('column.*', 'column x'), ('-At block line: [\\d]+, col: [\\d]+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^ ;
    execute block returns (y int) as
    begin
      for execute statement
          ('select rdb$relation_id from rdb$database where rdb$relation_id = :x') (1)
        with autonomous transaction
        into y
      do suspend;
    end ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -X
    -At line 1, column 67
    -At block line: 5, col: 3
  """

@pytest.mark.version('>=2.5.6')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

