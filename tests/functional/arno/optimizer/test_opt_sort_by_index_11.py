#coding:utf-8

"""
ID:          optimizer.sort-by-index-11
TITLE:       ORDER BY ASC using index (multi)
DESCRIPTION:
  ORDER BY X, Y
  When more fields are given in ORDER BY clause try to use a compound index.
FBTEST:      functional.arno.optimizer.opt_sort_by_index_11
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create or alter procedure sp_fill_data as begin end;
    recreate table test (
        id1 int,
        id2 int
    );

    set term ^;
    create or alter procedure sp_fill_data
    as
        declare x int;
        declare y int;
    begin
        x = 1;
        while (x <= 50) do
        begin
            y = (x / 10) * 10;
            insert into test(id1, id2) values(:y, :x - :y);
            x = x + 1;
        end
        insert into test (id1, id2) values (0, null);
        insert into test (id1, id2) values (null, 0);
        insert into test (id1, id2) values (null, null);
    end
    ^
    set term ;^
    commit;

    execute procedure sp_fill_data;
    commit;

    create asc  index test_id1_asc on test (id1);
    create desc index test_id1_des on test (id1);

    create asc  index test_id2_asc on test (id2);
    create desc index test_id2_des on test (id2);

    create asc  index test_id1_id2_asc on test (id1, id2);
    create desc index test_id1_id2_des on test (id1, id2);

    create asc  index test_id2_id1_asc on test (id2, id1);
    create desc index test_id2_id1_des on test (id2, id1);
    commit;

    set explain on;
    set planonly;

    select t.id2, t.id1
    from test t
    where t.id1 = 30 and t.id2 >= 5
    order by t.id2 asc, t.id1 asc
    ;

    select t.id2, t.id1
    from test t
    where t.id1 = 30 and t.id2 <= 5
    order by t.id2 desc, t.id1 desc
    ;

    select t.id2, t.id1
    from test t
    where t.id1 >= 30 and t.id2 = 5
    order by t.id2 asc, t.id1 asc
    ;

    select t.id2, t.id1
    from test t
    where t.id1 <= 30 and t.id2 = 5
    order by t.id2 desc, t.id1 desc
    ;



    select t.id2, t.id1
    from test t
    where t.id1 <= 30 and t.id2 <= 5
    order by t.id2 asc, t.id1 asc
    ;

    select t.id2, t.id1
    from test t
    where t.id1 <= 30 and t.id2 <= 5
    order by t.id2 desc, t.id1 desc
    ;

    select t.id2, t.id1
    from test t
    where t.id1 >= 30 and t.id2 >= 5
    order by t.id2 asc, t.id1 asc
    ;

    select t.id2, t.id1
    from test t
    where t.id1 >= 30 and t.id2 >= 5
    order by t.id2 desc, t.id1 desc
    ;

"""

act = isql_act('db', test_script)

expected_stdout = """
    Select Expression
        -> Sort (record length: 36, key length: 16)
            -> Filter
                -> Table "TEST" as "T" Access By ID
                    -> Bitmap
                        -> Index "TEST_ID1_ID2_ASC" Range Scan (lower bound: 2/2, upper bound: 1/2)

    Select Expression
        -> Sort (record length: 36, key length: 16)
            -> Filter
                -> Table "TEST" as "T" Access By ID
                    -> Bitmap
                        -> Index "TEST_ID1_ID2_ASC" Range Scan (lower bound: 1/2, upper bound: 2/2)

    Select Expression
        -> Filter
            -> Table "TEST" as "T" Access By ID
                -> Index "TEST_ID2_ID1_ASC" Range Scan (lower bound: 2/2, upper bound: 1/2)

    Select Expression
        -> Filter
            -> Table "TEST" as "T" Access By ID
                -> Index "TEST_ID2_ID1_DES" Range Scan (lower bound: 2/2, upper bound: 1/2)

    Select Expression
        -> Filter
            -> Table "TEST" as "T" Access By ID
                -> Index "TEST_ID2_ID1_ASC" Range Scan (upper bound: 1/2)
                    -> Bitmap
                        -> Index "TEST_ID1_ASC" Range Scan (upper bound: 1/1)

    Select Expression
        -> Filter
            -> Table "TEST" as "T" Access By ID
                -> Index "TEST_ID2_ID1_DES" Range Scan (lower bound: 1/2)
                    -> Bitmap
                        -> Index "TEST_ID1_ASC" Range Scan (upper bound: 1/1)

    Select Expression
        -> Filter
            -> Table "TEST" as "T" Access By ID
                -> Index "TEST_ID2_ID1_ASC" Range Scan (lower bound: 1/2)
                    -> Bitmap
                        -> Index "TEST_ID1_ASC" Range Scan (lower bound: 1/1)

    Select Expression
        -> Filter
            -> Table "TEST" as "T" Access By ID
                -> Index "TEST_ID2_ID1_DES" Range Scan (upper bound: 1/2)
                    -> Bitmap
                        -> Index "TEST_ID1_ASC" Range Scan (lower bound: 1/1)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
