#coding:utf-8
#
# id:           bugs.core_2812
# title:        Prohibit any improper mixture of explicit and implicit joins
# decription:   
# tracker_id:   CORE-2812
# min_versions: ['2.5.3']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', ''), ('-At line.*', '')]

init_script_1 = """
    recreate table t_left(id int);
    insert into t_left values(111);
    insert into t_left values(999);
    commit;
    
    recreate table t_right(id int, val int);
    insert into t_right values(111,0);
    insert into t_right values(999,123456789);
    commit;
    
    recreate table t_middle(id int);
    insert into t_middle values(1);
    commit;

    -- one more sample (after discussion with Dmitry by e-mail, 02-apr-2015 19:34)
    recreate table t1(id int); 
    commit;
    insert into t1 values( 1 ); 
    commit;

    recreate table test(x int);
    insert into test values(1);
    commit;


"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    select
         'case-1' as msg
        ,L.id proc_a_id
        ,m.id mid_id
        ,R.id b_id, R.val
    from t_left L
    
         ,  -- ::: nb ::: this is >>> COMMA <<< instead of `cross join`
         
         t_middle m
         left join t_right R on L.id=R.id
    ;
    
    select
        'case-2' as msg
        ,l.id a_id, m.id mid_id, r.id b_id, r.val
    from t_left l
        cross join t_middle m
        left join t_right r on l.id=r.id;

    -- Added 02-apr-2015:
    select 'case-3' msg, a.id 
    from t1 a
        , t1 b 
          join t1 c on a.id=c.id 
    where a.id=b.id; -- this FAILS on 3.0

    select 'case-4' msg, a.id 
    from t1 b
       , t1 a 
         join t1 c on a.id=c.id 
    where a.id=b.id; -- this WORKS on 3.0

    ---------------------------------------------------------

    -- Added 29-jun-2017, after reading CORE-5573:

    -- This should PASS:
    select 1 as z1
    from 
        test a
        join 
              test s
              inner join 
              (
                    test d 
                    join test e on e.x = d.x 
                    join ( test f join test g on f.x = g.x ) on e.x = g.x 
                    --- and f.x=s.x

              )
              on 1=1
        on g.x=d.x
    ;

    -- This should FAIL on 3.0+ (but is passes on 2.5):
    select 2 as z2
    from 
        test a
        join 
              test s
              inner join 
              (
                    test d 
                    join test e on e.x = d.x 
                    join ( test f join test g on f.x = g.x ) on e.x = g.x 
                    and f.x=s.x -- <<< !! <<<

              )
              on 1=1
        on g.x=d.x
    ;


"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             case-2
    A_ID                            111
    MID_ID                          1
    B_ID                            111
    VAL                             0

    MSG                             case-2
    A_ID                            999
    MID_ID                          1
    B_ID                            999
    VAL                             123456789

    MSG                             case-4
    ID                              1

    Z1                              1

"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -L.ID

    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -A.ID

    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code
    -Column unknown
    -S.X
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

