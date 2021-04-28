#coding:utf-8
#
# id:           bugs.core_4281
# title:        FB 3: TYPE OF arguments of stored functions will hang firebird engine if depending domain or column is changed
# decription:   
# tracker_id:   CORE-4281
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
    create domain testdomain as integer;
    commit;
    
    create function testfunction (arg1 type of testdomain) returns integer as
    begin
    end;
    
    commit;
    alter domain testdomain type bigint;
    commit; 
    
    show domain testdomain;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TESTDOMAIN                      BIGINT Nullable
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

