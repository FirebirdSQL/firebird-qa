#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/1670
TITLE:       Incorrect column values with outer joins and derived tables
DESCRIPTION:
NOTES:
    [20.02.2026] pzotov
    Re-implemented: FULL JOIN execution plan has changed since 19.02.2026 6.0.0.1458, commit:
    "6a76c1da Better index usage in full outer joins...".  This changed the order of rows in resultset.
    The fix is trivial: we can add 'ORDER BY' to the query and this must not change execution plan
    (i.e. optimizer still has to use FULL JOIN in this case! Discussed with dimitr, 20.02.2026 1345).

    Checked on 6.0.0.1461-5e98812; 6.0.0.1454-b45aa4e; 5.0.4.1767-52823f5; 4.0.7.3243; 3.0.14.33838
"""

import pytest
from firebird.qa import *

init_script = """
    create table t1 (n int);
    create table t2 (n int);

    insert into t1 values (1);
    insert into t1 values (2);
    insert into t2 values (2);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set list on;
    select t1.n as t1_n, t2.n as t2_n
    from (
        select 1 n from rdb$database
    ) t1
    full join (
        select 2 n from rdb$database
    ) t2 on t2.n = t1.n
    order by 1,2 -- <<< added 20.02.2026
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    T1_N                            <null>
    T2_N                            2

    T1_N                            1
    T2_N                            <null>
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

