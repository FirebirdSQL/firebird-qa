#coding:utf-8

"""
ID:          issue-1599
ISSUE:       1599
TITLE:       Crash on infinite mutual SP calls (instead of "Too many concurrent executions of the same request.")
DESCRIPTION:
JIRA:        CORE-4653
FBTEST:      bugs.core_4653
"""

import pytest
from firebird.qa import *

init_script = """
    set term ^;
    create or alter procedure p03(a_i int) returns (z int) as
    begin
      z = 0 ;
      suspend;
    end^
    commit^

    create or alter procedure p02(a_i int) returns (z int) as
    begin
      z = (select z from p03(:a_i)) + 1;
      suspend;
    end^
    commit^

    create or alter procedure p03(a_i int) returns (z int) as
    begin
      z = (select z from p02(:a_i)) + 1;
      suspend;
    end^
    commit^

    create or alter procedure p01(a_i int) returns (z int) as
    begin
      z = (select z from p02(:a_i)) + 1;
      suspend;
    end^
    commit^
    set term ;^
"""

db = db_factory(init=init_script)

test_script = """
  -- 07.03.2015: updated expected_stderr - it was changed and now is identical in 2.5 & 3.0
  -- Old stderr:
  -- Statement failed, SQLSTATE = HY001
  -- Stack overflow.  The resource requirements of the runtime stack have exceeded the memory available to it.

  select * from p01(1);
"""

act = isql_act('db', test_script, substitutions=[('=.*', ''), ('line.*', ''), ('col.*', '')])

expected_stdout = """
               Z
    ============
"""

expected_stderr = """
    Statement failed, SQLSTATE = 54001
    Too many concurrent executions of the same request
    -At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At procedure 'P02' line: 3, col: 3
    At procedure 'P03' line: 3, col: 3
    At p...
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

