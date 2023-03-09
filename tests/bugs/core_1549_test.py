#coding:utf-8

"""
ID:          issue-1966
ISSUE:       1966
TITLE:       Subquery-based predicates are not evaluated early in the join order
DESCRIPTION:
JIRA:        CORE-1549
FBTEST:      bugs.core_1549
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t(id int);
    commit;
    insert into t select row_number()over() from rdb$types a, (select 1 i from rdb$types rows 4) b rows 1000;
    commit;
    create index t_id on t(id);
    commit;

    -- Query-1:
    set list on;
    select '' as "EXISTS with ref. to 1st stream:" from rdb$database;

    set planonly;
    set explain on;

    select a.id a_id, b.id b_id
    from t a join t b on b.id >= a.id
    where
      not exists (select * from t x where x.id = a.id - 1)
      and
      not exists (select * from t z where z.id = b.id + 1);

    set planonly;
    set plan off;
    set explain off;

    select '' as "Two sep. DT and EXISTS inside:" from rdb$database;

    set planonly;
    set explain on;
    -- Query-2
    -- (serves as "etalone" -- how it should be in query-1):
    select a.id a_id, b.id b_id
    from (
        select t1.id
        from t t1
        where
            not exists (select * from t x where x.id = t1.id - 1)
    ) a
    join
    (
        select t2.id
        from t t2
        where
            not exists (select * from t x where x.id = t2.id + 1)
    ) b
    on b.id >= a.id;
"""

act = isql_act('db', test_script)

fb3x_expected_out = """
        EXISTS with ref. to 1st stream:

        Select Expression
            -> Filter
                -> Table "T" as "X" Access By ID
                    -> Bitmap
                        -> Index "T_ID" Range Scan (full match)
        Select Expression
            -> Filter
                -> Table "T" as "Z" Access By ID
                    -> Bitmap
                        -> Index "T_ID" Range Scan (full match)
        Select Expression
            -> Nested Loop Join (inner)
                -> Filter
                    -> Table "T" as "A" Full Scan
                -> Filter
                    -> Table "T" as "B" Access By ID
                        -> Bitmap
                            -> Index "T_ID" Range Scan (lower bound: 1/1)


        Two sep. DT and EXISTS inside:

        Select Expression
            -> Filter
                -> Table "T" as "B X" Access By ID
                    -> Bitmap
                        -> Index "T_ID" Range Scan (full match)
        Select Expression
            -> Filter
                -> Table "T" as "A X" Access By ID
                    -> Bitmap
                        -> Index "T_ID" Range Scan (full match)
        Select Expression
            -> Nested Loop Join (inner)
                -> Filter
                    -> Table "T" as "A T1" Full Scan
                -> Filter
                    -> Table "T" as "B T2" Access By ID
                        -> Bitmap
                            -> Index "T_ID" Range Scan (lower bound: 1/1)
"""

fb5x_expected_out = """
    EXISTS with ref. to 1st stream: 

    Sub-query
        -> Filter
            -> Table "T" as "X" Access By ID
                -> Bitmap
                    -> Index "T_ID" Range Scan (full match)
    Sub-query
        -> Filter
            -> Table "T" as "Z" Access By ID
                -> Bitmap
                    -> Index "T_ID" Range Scan (full match)
    Select Expression
        -> Nested Loop Join (inner)
            -> Filter
                -> Table "T" as "A" Full Scan
            -> Filter
                -> Table "T" as "B" Access By ID
                    -> Bitmap
                        -> Index "T_ID" Range Scan (lower bound: 1/1)

    Two sep. DT and EXISTS inside:  



    Sub-query
        -> Filter
            -> Table "T" as "B X" Access By ID
                -> Bitmap
                    -> Index "T_ID" Range Scan (full match)
    Sub-query
        -> Filter
            -> Table "T" as "A X" Access By ID
                -> Bitmap
                    -> Index "T_ID" Range Scan (full match)
    Select Expression
        -> Nested Loop Join (inner)
            -> Filter
                -> Table "T" as "A T1" Full Scan
            -> Filter
                -> Table "T" as "B T2" Access By ID
                    -> Bitmap
                        -> Index "T_ID" Range Scan (lower bound: 1/1)
"""
@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = fb3x_expected_out if act.is_version('<5') else fb5x_expected_out
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

