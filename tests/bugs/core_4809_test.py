#coding:utf-8

"""
ID:          issue-5107
ISSUE:       5107
TITLE:       HASH/MERGE JOIN is not used for more than two streams if they are joined via
  USING/NATURAL clauses and join is based on DBKEY concatenations
DESCRIPTION:
JIRA:        CORE-4809
FBTEST:      bugs.core_4809
NOTES:
    [07.04.2022] pzotov
    FB 5.0.0.455 and later: data sources with equal cardinality now present in the HASH plan in order they are specified in the query.
    Reversed order was used before this build. Because of this, two cases of expected stdout must be taken in account, see variables
    'fb3x_checked_stdout' and 'fb5x_checked_stdout'.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table tk(x int primary key using index tk_x);
    commit;
    insert into tk(x)
    with recursive r as (select 0 i from rdb$database union all select r.i+1 from r where r.i<99)
    select r1.i*100+r0.i from r r1, r r0;
    commit;
    set statistics index tk_x;
    commit;

    recreate table tf(id_key int primary key using index tf_id_key);
    commit;
    insert into tf(id_key)
    with recursive r as (select 0 i from rdb$database union all select r.i+1 from r where r.i<99)
    select r1.i*100+r0.i from r r1, r r0;
    commit;
    set statistics index tf_id_key;
    commit;

    set planonly;

    -- 1. Join using RDB$DB_KEY based expressions:

    ----------- test `traditional` join form -----------------

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    join (select rdb$db_key||'' a from tk) s on r.a = s.a;


    select count(*)
    from (select rdb$db_key||'' a from tk) r
    join (select rdb$db_key||'' a from tk) s on r.a = s.a
    join (select rdb$db_key||'' a from tk) t on s.a = t.a;


    select count(*)
    from (select rdb$db_key||'' a from tk) r
    join (select rdb$db_key||'' a from tk) s on r.a = s.a
    join (select rdb$db_key||'' a from tk) t on s.a = t.a
    join (select rdb$db_key||'' a from tk) u on t.a = u.a;

    ----------- test join on named columns form -----------------

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    join (select rdb$db_key||'' a from tk) s using(a);

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    join (select rdb$db_key||'' a from tk) s using(a)
    join (select rdb$db_key||'' a from tk) t using(a);

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    join (select rdb$db_key||'' a from tk) s using(a)
    join (select rdb$db_key||'' a from tk) t using(a)
    join (select rdb$db_key||'' a from tk) u using(a);

    ----------- test natural join form -----------------

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    natural join (select rdb$db_key||'' a from tk) s;

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    natural join (select rdb$db_key||'' a from tk) s
    natural join (select rdb$db_key||'' a from tk) t;

    select count(*)
    from (select rdb$db_key||'' a from tk) r
    natural join (select rdb$db_key||'' a from tk) s
    natural join (select rdb$db_key||'' a from tk) t
    natural join (select rdb$db_key||'' a from tk) u;

    -------------------------------------------------

    -- 2. Join using COMMON FIELD based expressions:
    -- (all following statements produced 'PLAN HASH' before fix also;
    --  here we verify them only for sure that evething remains OK).

    ----------- test `traditional` join form -----------------

    select count(*)
    from (select id_key||'' a from tf) r
    join (select id_key||'' a from tf) s on r.a = s.a;


    select count(*)
    from (select id_key||'' a from tf) r
    join (select id_key||'' a from tf) s on r.a = s.a
    join (select id_key||'' a from tf) t on s.a = t.a;


    select count(*)
    from (select id_key||'' a from tf) r
    join (select id_key||'' a from tf) s on r.a = s.a
    join (select id_key||'' a from tf) t on s.a = t.a
    join (select id_key||'' a from tf) u on t.a = u.a;

    ----------- test join on named columns form -----------------

    select count(*)
    from (select id_key||'' a from tf) r
    join (select id_key||'' a from tf) s using(a);

    select count(*)
    from (select id_key||'' a from tf) r
    join (select id_key||'' a from tf) s using(a)
    join (select id_key||'' a from tf) t using(a);

    select count(*)
    from (select id_key||'' a from tf) r
    join (select id_key||'' a from tf) s using(a)
    join (select id_key||'' a from tf) t using(a)
    join (select id_key||'' a from tf) u using(a);

    ----------- test natural join form -----------------

    select count(*)
    from (select id_key||'' a from tf) r
    natural join (select id_key||'' a from tf) s;

    select count(*)
    from (select id_key||'' a from tf) r
    natural join (select id_key||'' a from tf) s
    natural join (select id_key||'' a from tf) t;

    select count(*)
    from (select id_key||'' a from tf) r
    natural join (select id_key||'' a from tf) s
    natural join (select id_key||'' a from tf) t
    natural join (select id_key||'' a from tf) u;
"""

act = isql_act('db', test_script)

fb3x_checked_stdout = """
    PLAN HASH (S TK NATURAL, R TK NATURAL)
    PLAN HASH (HASH (T TK NATURAL, S TK NATURAL), R TK NATURAL)
    PLAN HASH (HASH (HASH (U TK NATURAL, T TK NATURAL), S TK NATURAL), R TK NATURAL)
    PLAN HASH (S TK NATURAL, R TK NATURAL)
    PLAN HASH (T TK NATURAL, HASH (S TK NATURAL, R TK NATURAL))
    PLAN HASH (U TK NATURAL, HASH (T TK NATURAL, HASH (S TK NATURAL, R TK NATURAL)))
    PLAN HASH (S TK NATURAL, R TK NATURAL)
    PLAN HASH (T TK NATURAL, HASH (S TK NATURAL, R TK NATURAL))
    PLAN HASH (U TK NATURAL, HASH (T TK NATURAL, HASH (S TK NATURAL, R TK NATURAL)))
    PLAN HASH (S TF NATURAL, R TF NATURAL)
    PLAN HASH (HASH (T TF NATURAL, S TF NATURAL), R TF NATURAL)
    PLAN HASH (HASH (HASH (U TF NATURAL, T TF NATURAL), S TF NATURAL), R TF NATURAL)
    PLAN HASH (S TF NATURAL, R TF NATURAL)
    PLAN HASH (T TF NATURAL, HASH (S TF NATURAL, R TF NATURAL))
    PLAN HASH (U TF NATURAL, HASH (T TF NATURAL, HASH (S TF NATURAL, R TF NATURAL)))
    PLAN HASH (S TF NATURAL, R TF NATURAL)
    PLAN HASH (T TF NATURAL, HASH (S TF NATURAL, R TF NATURAL))
    PLAN HASH (U TF NATURAL, HASH (T TF NATURAL, HASH (S TF NATURAL, R TF NATURAL)))
"""


fb5x_checked_stdout = """
    PLAN HASH (R TK NATURAL, S TK NATURAL)
    PLAN HASH (R TK NATURAL, S TK NATURAL, T TK NATURAL)
    PLAN HASH (R TK NATURAL, S TK NATURAL, T TK NATURAL, U TK NATURAL)
    PLAN HASH (R TK NATURAL, S TK NATURAL)
    PLAN HASH (HASH (R TK NATURAL, S TK NATURAL), T TK NATURAL)
    PLAN HASH (HASH (HASH (R TK NATURAL, S TK NATURAL), T TK NATURAL), U TK NATURAL)
    PLAN HASH (R TK NATURAL, S TK NATURAL)
    PLAN HASH (HASH (R TK NATURAL, S TK NATURAL), T TK NATURAL)
    PLAN HASH (HASH (HASH (R TK NATURAL, S TK NATURAL), T TK NATURAL), U TK NATURAL)
    PLAN HASH (R TF NATURAL, S TF NATURAL)
    PLAN HASH (R TF NATURAL, S TF NATURAL, T TF NATURAL)
    PLAN HASH (R TF NATURAL, S TF NATURAL, T TF NATURAL, U TF NATURAL)
    PLAN HASH (R TF NATURAL, S TF NATURAL)
    PLAN HASH (HASH (R TF NATURAL, S TF NATURAL), T TF NATURAL)
    PLAN HASH (HASH (HASH (R TF NATURAL, S TF NATURAL), T TF NATURAL), U TF NATURAL)
    PLAN HASH (R TF NATURAL, S TF NATURAL)
    PLAN HASH (HASH (R TF NATURAL, S TF NATURAL), T TF NATURAL)
    PLAN HASH (HASH (HASH (R TF NATURAL, S TF NATURAL), T TF NATURAL), U TF NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = fb3x_checked_stdout if act.is_version('<5') else fb5x_checked_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

