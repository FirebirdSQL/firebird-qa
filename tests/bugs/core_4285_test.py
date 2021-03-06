#coding:utf-8
#
# id:           bugs.core_4285
# title:        Choose the best matching index for navigation
# decription:   
#                   When ORDER plan is in game, the optimizer chooses the first index candidate that matches the ORDER BY / GROUP BY clause.
#                   This is not the best approach when multiple index choices are available
#               
#                   22.12.2019. Refactored: split code and expected_std* for each major FB version; add some data to the test table.
#                   Checked on:
#                       4.0.0.1694: 1.598s // NB: output in 4.0 became match to 3.x since 4.0.0.1694
#                       4.0.0.1637: 1.515s.
#                       3.0.5.33215: 1.094s.
#                       NB: 3.0.5.33212 - FAILED, another index(es) are chosen!
#               
#                  25.07.2020: removed section for 4.0 because expected size must be equal in both major FB version, as it is given for 3.0.
#                  (letter from dimitr, 25.07.2020 12:42). Checked on 3.0.7.33348, 4.0.0.2119
#               
#                
# tracker_id:   CORE-4285
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

