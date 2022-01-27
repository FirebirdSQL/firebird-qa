#coding:utf-8

"""
ID:          issue-6462
ISSUE:       6462
TITLE:       COUNT(DISTINCT <DECFLOAT_FIELD>) leads FB to crash when there are duplicate values of this field
DESCRIPTION:
JIRA:        CORE-6218
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(n decfloat);
    commit;

    insert into test values( 0 );
    insert into test values( 0 );
    commit;

    set list on;
    set explain on;

    select n as n_grouped_from_test0 from test group by 1; --- [ 1 ]
    select distinct n as n_uniq_from_test0 from test; -- [ 2 ]
    select count(distinct n) as count_uniq_from_test0 from test; -- [ 3 ]
"""

act = isql_act('db', test_script)

expected_stdout = """
    Select Expression
        -> Aggregate
            -> Sort (record length: 68, key length: 24)
                -> Table "TEST" Full Scan

    N_GROUPED_FROM_TEST0                                                     0



    Select Expression
        -> Unique Sort (record length: 68, key length: 24)
            -> Table "TEST" Full Scan

    N_UNIQ_FROM_TEST0                                                        0



    Select Expression
        -> Aggregate
            -> Table "TEST" Full Scan

    COUNT_UNIQ_FROM_TEST0           1
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
