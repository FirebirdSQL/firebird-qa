#coding:utf-8

"""
ID:          tabloid.join-transformation-06
TITLE:       Check ability of outer join simplification.
DESCRIPTION:
  We can replace 'A left join B' with 'A inner join B' if:
     1. Both of these datasources are referred later in the expression of INNER join with some else datasource, and
     2. There are no disjunction in this expression, i.e. its parts aren't linked by "OR", and
     3. Each part of this expression is null-rejected.
FBTEST:      functional.tabloid.join_transformation_006
NOTES:
    [25.11.2023] pzotov
    Writing code requires more care since 6.0.0.150: ISQL does not allow to specify THE SAME terminator twice,
    i.e.
    set term @; select 1 from rdb$database @ set term @; - will not compile ("Unexpected end of command" raises).
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='join-transformations.fbk')

test_script = """
    execute procedure sp_fill( 40, 30 );
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
            'select a.id, b.id, c.id, d.id, null, null
            from
            (
                ( t1 a
                  LEFT
                  join t2 b on a.x = b.y
                )
                  left join t3 c on a.y = c.z
            )
            inner join t4 d on a.v = d.w and b.z = d.u'
            -- ^-- INNER clause + absence of disjunction ("or"-parts) + null-rejecting of each parts ("a.v = d.w"; "b.z = d.u")
            --     makes this expression as whole null-rejecting.
           ,
            ---------------------- Query-2 (simplified and we assume that it ALWAYS produces the same result as Q1)
            'select a.id, b.id, c.id, d.id, null, null
            from
            (
                ( t1 a
                  INNER
                  join t2 b on a.x = b.y
                )
                  left join t3 c on a.y = c.z
            )
            inner join t4 d on a.v = d.w and b.z = d.u'
            --                 ^             ^
            --                 +-------------+------> these datasources can be INNER joined because they
            --                                        BOTH participate in null-rejecting expression.

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
    set term ;^
"""

act = isql_act('db', test_script)

expected_stdout = """
    RESULT                          Passed.
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
