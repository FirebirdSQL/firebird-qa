#coding:utf-8
#
# id:           bugs.core_4381
# title:        Incorrect line/column information in runtime errors
# decription:   
# tracker_id:   CORE-4381
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
set term ^;



create or alter procedure p1 returns (x integer) as
begin
                           select 
                                                 'a' 
                           from rdb$database 
                                             into x;
end
^

execute procedure p1
^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "a"
    -At procedure 'P1' line: 3, col: 28
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

