#coding:utf-8

"""
ID:          tabloid.join-transformation-08
TITLE:       Check ability of outer join simplification.
DESCRIPTION:
  From join-transformation-008.fbt:
     ===
     For two sources, S and T, which:
     1) are separated by at least one "intermediate" source G (e.g. which is just "after" S and is "before" T), and
     2) are involved into left join predicate P(S,T) which does not participate in disjunction ("OR"ed) expression
     -- one may to replace all LEFT joins starting from G and up to T with INNER ones.
     Join condition between S and its adjacent datasource (G) should be preserved as it is in original query.
     ===
     Additional case here: when a query has several predicates {P1, P2,..., Pn} that involves non-adjacent datasources
     and are null-rejected then we can replace left-outer joins with inner ones separately for each of {P1, P2,..., Pn}.
     Moreover, if some pair of them (say, Px and Py) have common "affecting area" (affects on the same datasources) then
     result of replacement for Px can be preserved even if some of aliases (affected by Px) are starting pair for Py
     (which could NOT be replaced if query would have only one Py) - this effect looks like "bin_or".
FBTEST:      functional.tabloid.join_transformation_008
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
    execute procedure sp_fill( 20, 20 );
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
            -- if query returns less columns.

            -- Here we have two predicates that "jumps" over more than one datasource,
            -- i.e. they involve relations which are NOT adjacent in the query.
            -- Hereafter such predicates are called "jumpers".
            -- First such predicate is "a.z = d.x" - it involve relations A & D and
            -- its affecting area is marked below as "::::::::::::::".
            -- Second is "b.w = e.y" - it involve relations B &E and its affecting area
            -- is marked as "%%%%%%%%%%%%%".
            -- Note that these areas are crossed, i.e. they have common portion:
            --      a       b       c       d       e
            --      :::::::::::::::::::::::::
            --              %%%%%%%%%%%%%%%%%%%%%%%%%
            --
            -- Note also that relation F is not affected by these predicates.
            -- Because all expressions are null-rejected, we can replace LEFT joins with INNER ones
            -- in the following places:
            -- 1) for predicate "a.z=d.x" - starting from 'b left join c' and up to 'c left join d';
            -- 2) for predicate "b.w=e.y" - starting from 'c left join d' and up to 'd left join d'.
            -- If 2nd predicate would be single that "jumps" over several datasources, then we could
            -- NOT to change 'b left join c' with inner. But we DO this when handle 1st "jumper", and
            -- this replacement (will be made for "a.z=d.x") is NOT discarded: this looks like "bin_or"
            -- result. In other words, if some LEFT_JOIN could be replaced with INNER one because of
            -- "jumping" predicate, this result shoudl be preserved during handling of further "jumpers".

            'select a.id, b.id, c.id, d.id, e.id, f.id
            from t1 a
                    LEFT
                    join t2 b
                            left
                            join t3 c
                                    left
                                    join t4 d
                                            left         -- +-- this alias is NOT afffected by any of "jumpers"!
                                            join t5 e    -- |
                                                    left -- |
                                                    join t6 F
                                                    on e.x = f.u
                                            on d.z = e.y
                                    on c.y = e.x
                            on b.w = e.y
                            -- %%%%%%%%% (2ns "jumper")
                    on a.z = d.x'
                    -- ::::::::: (1st "jumper")
            ,
            'select a.id, b.id, c.id, d.id, e.id, f.id
            from t1 a
                    LEFT -- this should be preserved anyway; explanation see in "join-transformation-008.fbt"
                    join t2 b
                            INNER -- "BIN_OR" here! This could NOT be done if we have only 2nd "jumper" (`b.w = e.y`) which STARTS from `b`.
                            --                               --    --  can be replaced because of jumper-1 ("a.z = d.x"); and this result will be PRESERVED despite of jumper-2.
                            join t3 c
                                    inner -- can be replaced because of jumper-2 ("b.w = e.y")
                                    join t4 d
                                            inner -- can be replaced because of jumper-2 ("b.w = e.y")
                                            join t5 e
                                                    LEFT -- <<< !! this should be preserved as OUTER join !!
                                                    join t6 F
                                                    on e.x = f.u
                                            on d.z = e.y
                                    on c.y = e.x
                            on b.w = e.y
                    on a.z = d.x'
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
