#coding:utf-8

"""
ID:          issue-4693
ISSUE:       4693
TITLE:       Create function/sp which references to non-existent exception <...>
DESCRIPTION:
JIRA:        CORE-4371
FBTEST:      bugs.core_4371
NOTES:
    [29.06.2025] pzotov
    Separated expected output for FB major versions prior/since 6.x.
    No substitutions are used to suppress schema and quotes. Discussed with dimitr, 24.06.2025 12:39.

    Checked on 6.0.0.876; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
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

substitutions = [('at offset \\d+', 'at offset')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout_5x = """
    Statement failed, SQLSTATE = 2F000
    Error while parsing function FN_TEST's BLR
    -invalid request BLR at offset
    -exception EX_SOME_NON_EXISTENT_NAME not defined
"""

expected_stdout_6x = """
    Statement failed, SQLSTATE = 2F000
    Error while parsing function "PUBLIC"."FN_TEST"'s BLR
    -invalid request BLR at offset
    -exception "PUBLIC"."EX_SOME_NON_EXISTENT_NAME" not defined
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
