#coding:utf-8
#
# id:           bugs.core_4653
# title:        Crash on infinite mutual SP calls (instead of "Too many concurrent executions of the same request.")
# decription:   20150108: crach every even run, WI-T3.0.0.31529, Win XP SP3
# tracker_id:   CORE-4653
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', ''), ('line.*', ''), ('col.*', '')]

init_script_1 = """
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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
  -- 07.03.2015: updated expected_stderr - it was changed and now is identical in 2.5 & 3.0
  -- Old stderr:
  -- Statement failed, SQLSTATE = HY001
  -- Stack overflow.  The resource requirements of the runtime stack have exceeded the memory available to it.

  select * from p01(1);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
               Z
    ============
"""
expected_stderr_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

