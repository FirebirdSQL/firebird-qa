#coding:utf-8
#
# id:           bugs.core_5393
# title:        Bad optimization of some operations with views containing subqueries
# decription:   
#                  Confirmed trouble on WI-V3.0.2.3262, ratio was ~146(!).
#                  Performance is OK  on WI-V3.0.2.32629 and WI-T4.0.0.450
#                  ::: NB:::
#                  Plans differ on 3.0.2 and 4.0 thus they are excluded from the output!
#                  Performance of 4.0 significantly _WORSE_ than of 3.0.2, sent letter to dimitr, 11.11.2016 13:47.
#                
# tracker_id:   CORE-5393
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view v_test as select 1 id from rdb$database;
    recreate view v_test1 as select 1 id from rdb$database;
    recreate view v_test2 as select 1 id from rdb$database;
    commit;

    recreate table test (id int primary key using index test_pk, col int);
    recreate table tlog(qt int, elap_ms int);
    commit;

    insert into test select row_number()over(),row_number()over()  from rdb$types,rdb$types rows 1000;
    --insert into test (id, col) values (1, 1);
    --insert into test (id, col) values (2, 2);
    commit;

    -- view must contain a subquery
    create or alter view v_test1 (id1, id2, col1, col2, dummy)
    as
    select t1.id, t2.id, t1.col, t2.col, (select 1 from rdb$database)
    from test t1 join test t2 on t1.col = t2.id;

    -- trigger makes the view updatable
    create or alter trigger trg_vtest1_bu for v_test1 before update as
    begin
    end;

    -- view must contain a subquery
    create or alter view v_test2 (id1, id2, col1, col2, dummy)
    as
    select ta.id, tb.id, ta.col, tb.col, (select 1 from rdb$database)
    from test ta join test tb on ta.col = tb.id;

    -- trigger makes the view updatable
    create or alter trigger trg_vtest2_bu
    for v_test2 before update
    as
    begin
    end;


    -- temply(?) disable ouput of plans: they DIFFER in 3.0.2 vs 4.0! -- set plan;

    set term ^;

    execute block as -- returns(elap_ms1 int) as
      declare t0 timestamp;
    begin
      t0='now';
      for select id1 from v_test1 as cursor c do
      begin
        update v_test1 x set x.col1 = 1
        where x.id1 = c.id1;
        -- where current of c;

        update v_test2 y set y.col1 = 1
        where y.id1 = c.id1;
      end
      insert into tlog(qt, elap_ms) values(1, datediff(millisecond from :t0 to cast('now' as timestamp)) ); 
    end
    ^

    execute block as -- returns(elap_ms2 int) as
      declare t0 timestamp;
    begin
      t0='now';
      for select id1 from v_test1 as cursor c do
      begin
        update v_test1 u set u.col1 = 1
        -- where id1 = c.id1;
        where current of c;

        update v_test2 v set v.col1 = 1
        where v.id1 = c.id1;
      end
      insert into tlog(qt, elap_ms) values(2, datediff(millisecond from :t0 to cast('now' as timestamp)) ); 
    end^
    set term ;^

    set list on;
    select iif( coalesce(ratio,0) < max_allowed, 
                'Acceptable', 
                'Poor ratio = ' 
                || cast(max_elap as varchar(20)) 
                || '/' || cast(min_elap as varchar(20)) 
                || ' = ' 
                || cast(ratio as varchar(20)) 
                || ' - more than max_allowed = ' || cast(max_allowed as varchar(20))
              )
           as ratio
    from (
      select 
         min(elap_ms) min_elap, 
         max(elap_ms) max_elap, 
         1.00 * max(elap_ms) / nullif(min(elap_ms),0) as ratio,
         2.30 as max_allowed
      --  ^
      --  |
      -- #################
      -- T H R E S H O L D
      -- #################
      from tlog
    );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RATIO                           Acceptable
  """

@pytest.mark.version('>=3.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

