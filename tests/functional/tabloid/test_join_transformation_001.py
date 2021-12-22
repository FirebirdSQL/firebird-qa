#coding:utf-8
#
# id:           functional.tabloid.join_transformation_001
# title:        Check ability of outer join simplification.
# decription:   Use null-rejected predicate, trivial case.
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='join-transformations.fbk', init=init_script_1)

test_script_1 = """
    execute procedure sp_fill( 25, 30 );
    --                         ^    ^- probability of assign each field on each row to NULL (percent).
    --                         +- number of rows in each of tables t1...t6

    commit;
    execute procedure sp_recalc_idx_stat;
    commit;
    
    set list on;
    set term ^;
    execute block returns(result varchar(50)) as
    begin
        select result
        from sp_run(
            ---------------------- Query-1 (not simplified)
            -- NB: we have to make "padding" of null literals up to 6 fields
            -- if query returns less columns:
            'select t1.id, t2.id, t3.id, t4.id, null, null
            from t1
            left join t2 on t1.x = t2.x
            left join t3 on t2.y = t3.y
            join t4 on t4.z not in( t1.u,  t2.v,  t3.w) and t4.y = t1.v'
          ,
            ---------------------- Query-2 (simplified and we assume that it ALWAYS produces the same result as Q1)
            'select t1.id, t2.id, t3.id, t4.id, null, null
            from t1
            inner join t2 on t1.x = t2.x
            inner join t3 on t2.y = t3.y
            inner join t4 on t4.z not in( t1.u,  t2.v,  t3.w) and t4.y = t1.v'
          , 0 ------------------------------------ nr_total: when 0 then do NOT run sp_fill because we already do have data for checking
        ) into result;

        suspend;

        if ( result not containing 'Passed' ) then
            -- this context variable serves as 'flag' to show 
            -- problematic data (see following EB):
            rdb$set_context('USER_SESSION', 'FAULT', '1'); 
    end
    ^
    execute block returns( failed_on varchar(255) ) as
    begin
        -- When queries are NOT equal on some data then we have to output
        -- rows from all tables in order to reproduce this trouble later:
        if ( rdb$get_context('USER_SESSION', 'FAULT') = '1' ) then
        begin
          for 
              select dml from sp_show_data 
              into failed_on
          do
              suspend;
        end
    end
    ^
    set term ^;


"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          Passed.
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

