#coding:utf-8

"""
ID:          issue-3455
ISSUE:       3455
TITLE:       Better performance for (table.field = :param or :param = -1) in where clause
DESCRIPTION:
  Test adds 20'000 rows into a table with single field and two indices on it (asc & desc).
  Indexed field will have values which will produce very poor selectivity (~1/3).
  Then we check number of indexed and natural reads using mon$ tables and prepared view
  from .fbk.
  We check cases when SP count rows using equality (=), IN and BETWEEN expr.
  When we pass NULLs then procedure should produce zero or low value (<100) of indexed reads.
  When we pass not null value then SP should produce IR with number ~ 1/3 of total rows in the table.
NOTES:
[15.05.2018]
  TODO LATER, using Python:
  Alternate code for possible checking (use trace with and ensure that only IR will occur when input arg is not null):

    set term ^;
    execute block as
    begin
      begin execute statement 'drop sequence g'; when any do begin end end
    end
    ^
    set term ;^
    commit;
    create sequence g;
    commit;

    create or alter procedure sp_test as begin end;
    commit;
    recreate table test(x int, y int);
    commit;

    insert into test select mod( gen_id(g,1), 123), mod( gen_id(g,1), 321)  from rdb$types,rdb$types rows 10000;
    commit;

    create index test_x on test(x);
    create index test_x_plus_y_asc on test computed by ( x - y );
    create descending index test_x_plus_y_dec on test computed by ( x+y );
    commit;

    set term ^;
    create or alter procedure sp_test( i1 int default null, i2 int default null ) as
        declare n int;
        declare s_x varchar(1000);
        declare s_y varchar(1000);
    begin
        s_x = 'select count(*) from test where x = :input_arg or :input_arg is null';
        s_y = 'select count(*) from test where x + y <= :input_sum  and   x - y >= :input_arg or :input_sum is null';
        execute statement (s_x) ( input_arg := :i1 ) into n;
        execute statement (s_y) ( input_arg := :i1, input_sum := :i2 ) into n;
    end
    ^
    set term ;^
    commit;

    execute procedure sp_test( 65, 99 );

  Trace log should contain following statistics for two ES:

    Table                              Natural     Index
    *****************************************************
    TEST                                              82

    Table                              Natural     Index
    *****************************************************
    TEST                                              90
JIRA:        CORE-3076
FBTEST:      bugs.core_3076
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='mon-stat-gathering-3_0.fbk')

test_script = """
    set bail on;
    set term ^;
    execute block as
    begin
      execute statement 'drop sequence g';
      when any do begin end
    end
    ^
    set term ;^
    commit;
    create sequence g;
    commit;

    create or alter procedure sp_test_x as begin end;
    create or alter procedure sp_test_y as begin end;
    commit;

    recreate table test(x int, y int);
    recreate table tcnt(q int); -- this serves only for storing total number of rows in 'TEST' table.
    commit;

    set term ^ ;
    create or alter procedure sp_test_x(arg_a int, arg_b int) -- for testing ASCENDING index
    as
        declare c int;
    begin
        if ( :arg_a = 0 ) then
            select count(*) from test where x = :arg_a or :arg_a is null into c;
        else if ( :arg_a = 1 ) then
            select count(*) from test where x in (:arg_a, :arg_b) or :arg_a is null into c;
        else
            select count(*) from test where x between :arg_a and :arg_b or :arg_a is null into c;
    end
    ^
    create or alter procedure sp_test_y(arg_a int, arg_b int) -- for testing DESCENDING index
    as
        declare c int;
    begin
        if ( :arg_a = 0 ) then
            select count(*) from test where y = :arg_a or :arg_a is null into c;
        else if ( :arg_a = 1 ) then
            select count(*) from test where y in (:arg_a, :arg_b) or :arg_a is null into c;
        else
            select count(*) from test where y between :arg_a and :arg_b or :arg_a is null into c;
    end
    ^
    set term ; ^
    commit;

    insert into test (x, y)
    select mod( gen_id(g,1), 3 ), mod( gen_id(g,1), 3 )
    from rdb$types, rdb$types
    rows 20000;
    insert into tcnt(q) select count(*) from test;
    commit;

    create index test_x on test(x);
    create descending index test_y on test(y);
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey'; -- mandatory!

    execute procedure sp_truncate_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    execute procedure sp_test_x(0, 0); ----- 1: where x = 0 or 0 is null // 'x' has ascending index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    execute procedure sp_test_y(0, 0); ----- 2: where y = 0 or 0 is null // 'y' has descend index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    execute procedure sp_test_x(1, 1); ----- 3: where x in (1, 1) or 1 is null // 'x' has ascending index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    execute procedure sp_test_y(1, 1); ----- 4: where y in (1, 1) or 1 is null // 'y' has descend index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------


    execute procedure sp_gather_stat;
    commit;

    execute procedure sp_test_x(2, 2); ----- 5: where x between 2 and 2 or 2 is null // 'x' has ascending index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    execute procedure sp_test_y(2, 2); ----- 6: where y between 2 and 2 or 2 is null // 'y' has descend index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    -- check that asc index will NOT be in use when count for :a is null
    execute procedure sp_test_x(null, null); -- 7: where x between NULL and NULL or NULL is null // 'x' has ascending index

    execute procedure sp_gather_stat;
    commit;

    --------------------------------

    execute procedure sp_gather_stat;
    commit;

    -- check that desc index will NOT be in use when count for :a is null
    execute procedure sp_test_y(null, null); -- 8: : where y between NULL and NULL or NULL is null // 'y' has descend index

    execute procedure sp_gather_stat;
    commit;

    SET LIST ON;
    select *
    from (
        select
            'When input arg is NOT null' as what_we_check,
            rowset,
            iif( natural_reads <= nr_threshold
                 and indexed_reads - total_rows/3.00 < ir_threshold -- max detected IR was: 6685 for c.total_rows=20'000
                ,'OK'
                ,'POOR:'||
                 ' NR=' || coalesce(natural_reads, '<null>') ||
                 ', IR='|| coalesce(indexed_reads, '<null>') ||
                 ', ir-cnt/3='|| coalesce(indexed_reads - total_rows/3.00, '<null>')
               ) as result
        from (
            select
                v.rowset
                ,v.natural_reads
                ,v.indexed_reads
                ,c.q as total_rows
                ,iif( rdb$get_context('SYSTEM','ENGINE_VERSION') starting with '3.', 0, 2 ) as nr_threshold -- max detected NR=2 for 4.0 (SS, CS)
                ,iif( rdb$get_context('SYSTEM','ENGINE_VERSION') starting with '3.', 45, 45 ) as ir_threshold -- max detected=44 for 4.0 (SS, CS)
            from v_agg_stat v cross join tcnt c
            where rowset <= 6
        )

        UNION ALL

        select
            'When input arg is NULL' as what_we_check,
            rowset,
            iif( natural_reads = total_rows
                 and indexed_reads < 100 -- 27.07.2016: detected IR=13 for FB 4.0.0.313
                ,'OK'
                ,'POOR:'||
                 ' NR=' || coalesce(natural_reads, '<null>') ||
                 ', IR='|| coalesce(indexed_reads, '<null>')
               ) as result
        from (
            select v.rowset, v.natural_reads, v.indexed_reads, c.q as total_rows
            from v_agg_stat v cross join tcnt c
            where rowset > 6
        )
    )
    order by rowset;
"""

act = isql_act('db', test_script)

expected_stdout = """
    WHAT_WE_CHECK                   When input arg is NOT null
    ROWSET                          1
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NOT null
    ROWSET                          2
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NOT null
    ROWSET                          3
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NOT null
    ROWSET                          4
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NOT null
    ROWSET                          5
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NOT null
    ROWSET                          6
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NULL
    ROWSET                          7
    RESULT                          OK

    WHAT_WE_CHECK                   When input arg is NULL
    ROWSET                          8
    RESULT                          OK
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

