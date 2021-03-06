#coding:utf-8
#
# id:           bugs.core_4755
# title:        Parameterized exception: wrong output when number of arguments greater than 7
# decription:   
# tracker_id:   CORE-4755
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_SOMETHING_WRONG
    -Arguments for raising exeption:  10001  10002  10003  10004  10005  10006  10007  10008  10009
    -At block line: 12, col: 5
    Statement failed, SQLSTATE = 07002
    Number of arguments (10) exceeds the maximum (9) number of EXCEPTION USING arguments
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

