#coding:utf-8
#
# id:           bugs.core_3618
# title:        Window Function: ntile(num_buckets integer)
# decription:   
#                  Cheched on 4.0.0.318.
#                
# tracker_id:   CORE-3618
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('line \\d+, column \\d+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(x int, y int, unique(x,y) using index test_unq_x_y);
    commit;

    insert into test values(null, null);
    insert into test values(null, null);
    insert into test values(null, null);
    insert into test values(null, 101);
    insert into test values(null, 102);
    insert into test values(null, 103);
    insert into test values(null, 104);
    insert into test values(1111, 105);
    insert into test values(1112, 106);
    commit;
    set list on;
    -- from doc: NTILE argument is restricted to
    -- integral positive literal, 
    -- variable (:var) 
    -- and DSQL parameter (question mark).

    -- This should PASS (even when argument is specified with decimal dot, but without scale):
    select x,y,ntile(3.)over(order by x,y) as n from test order by x,y;

    -- This should PASS:
    set term ^;
    execute block as
      declare n int = 3;
      declare c int;
    begin
      select count(*)
      from (
        select ntile( :n )over(order by x, y) as i from test
      ) x
      where x.i = :n
      into c;
    end
    ^

    -- This should PASS:
    execute block returns(x int, y int, n int) as 
    begin 
        for 
            execute statement ( 'select x,y, ntile(?)over(order by x, y) from test' ) ( 2 ) 
            into x,y,n 
        do 
            suspend; 
    end^ 
    set term ;^

    -- These should FAIL:
    select x,y,ntile(null)over(order by x) from test;
    select x,y,ntile(0)over(order by x) from test;
    select x,y,ntile(-1)over(order by x) from test;
    select x,y,ntile(3.0)over(order by x) from test order by x,y;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               <null>
    Y                               <null>
    N                               1
    X                               <null>
    Y                               <null>
    N                               1
    X                               <null>
    Y                               <null>
    N                               1
    X                               <null>
    Y                               101
    N                               2
    X                               <null>
    Y                               102
    N                               2
    X                               <null>
    Y                               103
    N                               2
    X                               <null>
    Y                               104
    N                               3
    X                               1111
    Y                               105
    N                               3
    X                               1112
    Y                               106
    N                               3

    X                               <null>
    Y                               <null>
    N                               1
    X                               <null>
    Y                               <null>
    N                               1
    X                               <null>
    Y                               <null>
    N                               1
    X                               <null>
    Y                               101
    N                               1
    X                               <null>
    Y                               102
    N                               1
    X                               <null>
    Y                               103
    N                               2
    X                               <null>
    Y                               104
    N                               2
    X                               1111
    Y                               105
    N                               2
    X                               1112
    Y                               106
    N                               2
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown -
    -null

    Statement failed, SQLSTATE = 42000
    Argument #1 for NTILE must be positive

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown -
    --

    Statement failed, SQLSTATE = 42000
    Arguments for NTILE must be integral types or NUMERIC/DECIMAL without scale
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

