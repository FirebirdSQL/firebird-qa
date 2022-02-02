#coding:utf-8

"""
ID:          issue-5059
ISSUE:       5059
TITLE:       Parameterized exception: wrong output when number of arguments greater than 7
DESCRIPTION:
JIRA:        CORE-4755
FBTEST:      bugs.core_4755
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
	recreate exception ex_something_wrong 'Arguments for raising exeption:  @1  @2  @3  @4  @5  @6  @7  @8  @9';
	commit;
	set term ^;
	execute block as
	  declare v_1 int = 10001;
	  declare v_2 int = 10002;
	  declare v_3 int = 10003;
	  declare v_4 int = 10004;
	  declare v_5 int = 10005;
	  declare v_6 int = 10006;
	  declare v_7 int = 10007;
	  declare v_8 int = 10008;
	  declare v_9 int = 10009;
	begin
	   exception ex_something_wrong using(
          v_1
         ,v_2
         ,v_3
         ,v_4
         ,v_5
         ,v_6
         ,v_7
         ,v_8
         ,v_9
      );
    end
    ^
    set term ;^
    commit;

    recreate exception ex_too_much_detailed 'Arguments for raising exeption:  @1  @2  @3  @4  @5  @6  @7  @8  @9  @10';
    commit;
    set term ^;
    execute block as
      declare v_1 int = 10001;
      declare v_2 int = 10002;
      declare v_3 int = 10003;
      declare v_4 int = 10004;
      declare v_5 int = 10005;
      declare v_6 int = 10006;
      declare v_7 int = 10007;
      declare v_8 int = 10008;
      declare v_9 int = 10009;
      declare v_10 int = 10010;
    begin
       exception ex_too_much_detailed using(
          v_1
         ,v_2
         ,v_3
         ,v_4
         ,v_5
         ,v_6
         ,v_7
         ,v_8
         ,v_9
         ,v_10
      );
    end
    ^
    set term ;^
"""

act = isql_act('db', test_script, substitutions=[('-At block line: [\\d]+, col: [\\d]+',
                                                  '-At block line')])

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_SOMETHING_WRONG
    -Arguments for raising exeption:  10001  10002  10003  10004  10005  10006  10007  10008  10009
    -At block line: 12, col: 5
    Statement failed, SQLSTATE = 07002
    Number of arguments (10) exceeds the maximum (9) number of EXCEPTION USING arguments
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

