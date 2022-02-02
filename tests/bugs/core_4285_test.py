#coding:utf-8

"""
ID:          issue-4608
ISSUE:       4608
TITLE:       Choose the best matching index for navigation
DESCRIPTION:
JIRA:        CORE-4285
FBTEST:      bugs.core_4285
"""

import pytest
from firebird.qa import *

init_script = """
    set bail on;
    recreate table test (col1 int, col2 int, col3 int);
    commit;
    insert into test(col1, col2, col3)
    with recursive
    r as (
        select 0 as i from rdb$database
        union all
        select r.i+1 from r
        where r.i < 49
    )
    select mod(r1.i,1000), mod(r1.i,100), mod(r1.i,10)
    from r as r1, r as r2
    where 1=1
    ;
    commit;

    create index test_col1 on test (col1);
    create index test_col12 on test (col1, col2);
    create index test_col21 on test (col2, col1);
    create index test_col123 on test (col1, col2, col3);
    create index test_col132 on test (col1, col3, col2);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set explain on;
    set planonly;
    set echo on;

    select 1 from test order by col1;

    ------
    select 1 from test where col1 = 0 order by col1;

    ------
    select 1 from test order by col1, col2;

    ------
    select 1 from test where col1 = 0 order by col1, col2;

    ------
    select 1 from test where col1 = 0 and col2 = 0 order by col1, col2;

    ------
    select 1 from test order by col1, col2, col3;

    ------
    select 1 from test where col1 = 0 order by col1, col2, col3;

    ------
    select 1 from test where col1 = 0 and col2 = 0 order by col1, col2, col3;

    ------
    select 1 from test where col1 = 0 and col3 = 0 order by col1;

    ------
    select 1 from test where col1 = 0 and col3 = 0 order by col1, col2, col3;

    ------
    select 1 from test where col1 = 0 and col3 = 0 order by col1, col3;

"""

act = isql_act('db', test_script)

expected_stdout = """
    select 1 from test order by col1;

    Select Expression
        -> Table "TEST" Access By ID
            -> Index "TEST_COL1" Full Scan

    ------
    select 1 from test where col1 = 0 order by col1;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL1" Range Scan (full match)

    ------
    select 1 from test order by col1, col2;

    Select Expression
        -> Table "TEST" Access By ID
            -> Index "TEST_COL12" Full Scan

    ------
    select 1 from test where col1 = 0 order by col1, col2;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL12" Range Scan (partial match: 1/2)

    ------
    select 1 from test where col1 = 0 and col2 = 0 order by col1, col2;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL12" Range Scan (full match)

    ------
    select 1 from test order by col1, col2, col3;

    Select Expression
        -> Table "TEST" Access By ID
            -> Index "TEST_COL123" Full Scan

    ------
    select 1 from test where col1 = 0 order by col1, col2, col3;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL123" Range Scan (partial match: 1/3)

    ------
    select 1 from test where col1 = 0 and col2 = 0 order by col1, col2, col3;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL123" Range Scan (partial match: 2/3)

    ------
    select 1 from test where col1 = 0 and col3 = 0 order by col1;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL132" Range Scan (partial match: 2/3)

    ------
    select 1 from test where col1 = 0 and col3 = 0 order by col1, col2, col3;

    Select Expression
        -> Sort (record length: 44, key length: 24)
            -> Filter
                -> Table "TEST" Access By ID
                    -> Bitmap
                        -> Index "TEST_COL132" Range Scan (partial match: 2/3)

    ------
    select 1 from test where col1 = 0 and col3 = 0 order by col1, col3;

    Select Expression
        -> Filter
            -> Table "TEST" Access By ID
                -> Index "TEST_COL132" Range Scan (partial match: 2/3)

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
