#coding:utf-8
#
# id:           bugs.core_6496
# title:        string_to_datetime and '\\0' symbol
# decription:   
#                   ascii_char(0) was allowed to be concatenated with string and pass then to cast(... as timestamp)
#                   up to 4.0.0.1227 (29-09-2018), and is forbidden since 4.0.0.1346 (17.12.2018).
#                   FB 3.x allows this character to be used and issues timestamp instead of error.
#                 
# tracker_id:   CORE-6496
# min_versions: ['4.0']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
  set heading off;
  select cast('5.3.2021 01:02:03.1234' || ascii_char(0) as timestamp) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22009
    Invalid time zone region:
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

