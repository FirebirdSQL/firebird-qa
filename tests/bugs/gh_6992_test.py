#coding:utf-8

"""
ID:          issue-6992
ISSUE:       6992
TITLE:       Transform OUTER joins into INNER ones if the WHERE condition violates the outer join rules
NOTES:
    [17.02.2023] pzotov
    Initial implementation. Additional tests will be added further.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    recreate table tmain(
        id int primary key using index tmain_pk
    );

    recreate table tdetl_a(
        id int primary key using index tdetl_a_pk
        ,pid int
        ,constraint tdetl_a_fk foreign key(pid) references tmain(id) using index tdetl_a_fk
    );

    recreate table tdetl_b(
        id int primary key using index tdetl_b_pk
        ,pid int NOT NULL
        ,constraint tdetl_b_fk foreign key(pid) references tmain(id) using index tdetl_b_fk
    );


    insert into tmain(id)
    select row_number()over() as i
    from rdb$types
    rows 20
    ;

    insert into tdetl_a(id, pid)
    select i, iif(mod(i,3)=0, null, 1 + mod(i,20))
    from (
        select row_number()over() as i
        from rdb$types, rdb$types
        rows 10000
    );
    insert into tdetl_b select id,coalesce(pid,1) from tdetl_a;
    commit;

    set statistics index tmain_pk;
    set statistics index tdetl_a_fk;
    set statistics index tdetl_b_fk;

    set planonly;
    set explain on;

    -- This must NOT be transformed because we make here ANTI-JOIN.
    -- Outer join is the only way to get proper result here:
    select *
    from tmain m1
    left join tdetl_a d1 on m1.id = d1.pid
    where d1.pid is null
    ;

    -- This MUST be transformed to INNER join because WHERE expression effectively will skip nulls.
    -- See also issue in the ticket:
    -- "regular comparisons that ignore NULLs by their nature, will cause the LEFT->INNER transformation"
    select *
    from tmain m2
    left join tdetl_a d2 on m2.id = d2.pid
    where d2.pid  = 0
    ;

    -- This must NOT be transformed, see ticket:
    -- "checks for NULL, e.g. WHERE T2.ID IS NOT NULL ..., would not transform LEFT into INNER"
    select *
    from tmain m3
    left join tdetl_a d3 on m3.id = d3.pid
    where d3.pid is not null
    ;

    -- This must NOT be transformed, reason is the same:
    -- "checks for NULL, e.g. WHERE T2.ID IS NOT NULL ..., would not transform LEFT into INNER"
    -- NB: the fact that column tdetl_b.pid is declared as NOT NULL is ignored here.
    -- This limitation seems redunant here.
    select *
    from tmain m4
    left join tdetl_b d4 on m4.id = d4.pid
    where d4.pid is not null
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    Select Expression
        -> Filter
            -> Nested Loop Join (outer)
                -> Table "TMAIN" as "M1" Full Scan
                -> Filter
                    -> Table "TDETL_A" as "D1" Access By ID
                        -> Bitmap
                            -> Index "TDETL_A_FK" Range Scan (full match)

    Select Expression
        -> Nested Loop Join (inner)
            -> Filter
                -> Table "TMAIN" as "M2" Access By ID
                    -> Bitmap
                        -> Index "TMAIN_PK" Unique Scan
            -> Filter
                -> Table "TDETL_A" as "D2" Access By ID
                    -> Bitmap
                        -> Index "TDETL_A_FK" Range Scan (full match)

    Select Expression
        -> Filter
            -> Nested Loop Join (outer)
                -> Table "TMAIN" as "M3" Full Scan
                -> Filter
                    -> Table "TDETL_A" as "D3" Access By ID
                        -> Bitmap
                            -> Index "TDETL_A_FK" Range Scan (full match)

    Select Expression
        -> Filter
            -> Nested Loop Join (outer)
                -> Table "TMAIN" as "M4" Full Scan
                -> Filter
                    -> Table "TDETL_B" as "D4" Access By ID
                        -> Bitmap
                            -> Index "TDETL_B_FK" Range Scan (full match)
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
