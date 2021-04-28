#coding:utf-8
#
# id:           bugs.core_5768
# title:        Implement FILTER-clause for aggregate functions (introduced in SQL:2003). This syntax allows for filtering before aggregation.
# decription:   
#                    Checked on 4.0.0.1249: OK.
#                
# tracker_id:   CORE-5768
# min_versions: ['4.0.0']
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
    recreate table test(x int, y int, q int);
    commit;
    insert into test(x,y,q) values(null, null, 100);
    insert into test(x,y,q) values(null, null, 200);
    insert into test(x,y,q) values(1000, null, 111);
    insert into test(x,y,q) values(1000, null, 222);
    insert into test(x,y,q) values(1000, 1000, 555);
    insert into test(x,y,q) values(1000, 1000, 777);
    commit;
    set list on;
    select 
         sum( iif(x is null, q, null) ) sum_q_iif_x_is_null
        ,sum( q )filter( where x is null ) sum_q_filter_x_is_null
        ,min( sum_q_iif_y_is_null_over ) filter( where true ) chk_filter_where_true
        ,min( sum_q_filter_y_is_null_over ) filter( where null is null ) chk_filter_where_n_is_n
        ,min( 1 ) filter( where null ) chk_filter_where_null ------------------------------------- allowed! boolean but without left part ?..
        ,min( 1 ) filter( where not null ) chk_filter_where_not_null
    from (
        select x, y, q
        ,sum( iif(y is null, q, null) ) over() sum_q_iif_y_is_null_over 
        ,sum( q )filter( where y is null) over() sum_q_filter_y_is_null_over
        from test
    )
    ;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SUM_Q_IIF_X_IS_NULL             300
    SUM_Q_FILTER_X_IS_NULL          300
    CHK_FILTER_WHERE_TRUE           633
    CHK_FILTER_WHERE_N_IS_N         633
    CHK_FILTER_WHERE_NULL           <null>
    CHK_FILTER_WHERE_NOT_NULL       <null>
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

