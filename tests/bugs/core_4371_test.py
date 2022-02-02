#coding:utf-8

"""
ID:          issue-4693
ISSUE:       4693
TITLE:       Create function/sp which references to non-existent exception <...>
DESCRIPTION:
JIRA:        CORE-4371
FBTEST:      bugs.core_4371
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stderr = """
Statement failed, SQLSTATE = 2F000
Error while parsing function FN_TEST's BLR
-invalid request BLR at offset 55
-exception EX_SOME_NON_EXISTENT_NAME not defined
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

