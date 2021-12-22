#coding:utf-8
#
# id:           bugs.core_4371
# title:        Create function/sp which references to non-existent exception <...>
# decription:   
# tracker_id:   CORE-4371
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
  create or alter function fn_test returns int as begin end^
  set term ;^
  commit;

  set term ^;
  create or alter function fn_test returns int as
  begin
    exception ex_some_non_existent_name;
    return 1;
  end
  ^
  set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
Statement failed, SQLSTATE = 2F000
Error while parsing function FN_TEST's BLR
-invalid request BLR at offset 55
-exception EX_SOME_NON_EXISTENT_NAME not defined
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

