#coding:utf-8
#
# id:           bugs.core_5606
# title:        Add expression index name to exception message if computation failed
# decription:   
#                  24.08.2020: changed sequence of actions: one statement must violate requirements of only ONE index.
#                  Before this statement:
#                      insert into test(id, x, y, s) values( 4, 3, -7, 'qwerty' );
#                  -- did violate TWO indices: test_eval3 and test_eval5.
#                  The order of which of them will raise first is undefined, so this test could fail because of appearance
#                  "wrong" index name in its STDERR. Detected on 4.0.0.2173. Discussed with hvlad, letter 23.08.2020 16:58.
#               
#                  Checked on 4.0.0.2173.
#                
# tracker_id:   CORE-5606
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
      id int
      ,x int
      ,y int
      ,r double precision
      ,s varchar(12) default 'DB_NAME'
    );
    create index test_eval1 on test computed by ( x/id );
    insert into test(id, x) values(0, 1);
    rollback;
    drop index test_eval1;

    create index test_eval2 on test computed by ( log10(r-15) );
    insert into test(id, r) values(1, 12);
    rollback;
    drop index test_eval2;

    create index test_eval3 on test computed by ( rdb$get_context('SYSTEM', s ) );
    insert into test(id, s) values(2, 'FOO_&_BAR');
    rollback;
    drop index test_eval3;

    create index test_eval4 on test computed by ( mod(x , (y-x) ) );
    insert into test(id, x, y) values(3, 10, 10);
    rollback;
    drop index test_eval4;

    create index test_eval5 on test computed by ( substring(s from x for id+y)  );
    insert into test(id, x, y, s) values( 4, 3, -7, 'qwerty' );
    drop index test_eval5;

    set count on;
    set list on;
    select id, s from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22012
    Expression evaluation error for index "TEST_EVAL1" on table "TEST"
    -arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.

    Statement failed, SQLSTATE = 42000
    Expression evaluation error for index "TEST_EVAL2" on table "TEST"
    -expression evaluation not supported
    -Argument for LOG10 must be positive

    Statement failed, SQLSTATE = HY000
    Expression evaluation error for index "TEST_EVAL3" on table "TEST"
    -Context variable FOO_&_BAR is not found in namespace SYSTEM
    Statement failed, SQLSTATE = 22012

    Expression evaluation error for index "TEST_EVAL4" on table "TEST"
    -arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.

    Statement failed, SQLSTATE = 22011
    Expression evaluation error for index "TEST_EVAL5" on table "TEST"
    -Invalid length parameter -3 to SUBSTRING. Negative integers are not allowed.
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

