#coding:utf-8

"""
ID:          issue-7257
ISSUE:       7257
TITLE:       Support for partial indices
NOTES:
    Initial discussion: https://github.com/FirebirdSQL/firebird/issues/3750
    Checked on 5.0.0.957 (intermediate build).
    NB. Currently this test contains only trivial cases for check.
    More complex examples, including misc datatypes (non-ascii, decfloat and int128),
    will be added later.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;

    -- test #1: FB must not crash when we create computed-by index which is PARTIAL
    -- and has the same field that is specified in the computed-by expression.
    -- https://github.com/FirebirdSQL/firebird/commit/8f12020e254d064f272a64e905ff4c4ed4777c3a
    recreate table test(
        id int primary key
        ,f01 int
        ,f02 int
    );

    -- this must pass:
    create index test_f01 on test computed by (f01)
    where f01 = 1 --------------------------------- [ ! ]
    ;
    commit;

    --#####################################################

    -- test #2: check usage of partial indices:
    recreate table test(
        id int primary key
        ,f01 int
        ,f02 int
    );
    insert into test(id, f01, f02)
    select i, iif(mod(i,100) < 2, 1, 2), iif(mod(i,150) < 2, 2, 1)
    from (
        select row_number()over() as i
        from rdb$types
        rows 200
    );
    commit;
    create index test_f01 on test(f01) where f01 = 2;
    create index test_f02 on test computed by (f02+f01) where f02+f01 = 3;

    set plan on;
    --set explain on;
    -- these must use natural scan:
    select count(*) from test where f01 = 1;
    select count(*) from test where f02 = 2;
    -- these must use index:
    select count(*) from test where f01 = 2;
    select count(*) from test where f01 + f02 = 3;
    set plan off;
    commit;

    --#####################################################

    -- test #3: check descending index when it is PARTIAL.
    -- See also letter to dimitr, 17.02.2023 21:11.
    -- https://github.com/FirebirdSQL/firebird/commit/c596b76e40b3c03e712135444d82e20091f9a178
    recreate table test(
        id int primary key
        ,f01 int
    );
    insert into test(id, f01)
    select i, iif( mod(i,20) < 19, null, i*i )
    from (
        select row_number()over() as i
        from rdb$types, rdb$types
        rows 200
    );
    commit;
     
    create ascending index test_computed_asc on test (f01) where f01 is null;
    create descending index test_computed_dec on test (f01) where f01 is null;
     
    set plan on;
     
    -- test NAVIGATION:
    select count(*) from (select id from test where f01 is null order by f01 asc ); -- must issue: 190
    select count(*) from (select id from test where f01 is null order by f01 desc); -- must issue: 190
     
    -- test BITMAP:
    select count(*) from test where f01 is null; -- must issue: 190
    alter index test_computed_asc inactive;
     
    select count(*) from test where f01 is null; -- must issue: 190 - BUT issued 0 before fix.
    set plan off;

"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (TEST NATURAL)
    COUNT                           4

    PLAN (TEST NATURAL)
    COUNT                           3

    PLAN (TEST INDEX (TEST_F01))
    COUNT                           196

    PLAN (TEST INDEX (TEST_F02))
    COUNT                           195


    PLAN (TEST ORDER TEST_COMPUTED_ASC)
    COUNT                           190

    PLAN (TEST ORDER TEST_COMPUTED_DEC)
    COUNT                           190

    PLAN (TEST INDEX (TEST_COMPUTED_ASC))
    COUNT                           190

    PLAN (TEST INDEX (TEST_COMPUTED_DEC))
    COUNT                           190
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
