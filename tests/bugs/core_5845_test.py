#coding:utf-8

"""
ID:          issue-6106
ISSUE:       6106
TITLE:       ORDER BY on index can cause suboptimal index choices
DESCRIPTION:
JIRA:        CORE-5845
FBTEST:      bugs.core_5845
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test
    (
        id1 integer,
        id2 integer,
        id3 integer,
        x numeric(18,2),
        constraint pk_test primary key(id1, id2, id3)
    );
    create index ixa_test__x on test(x);
    create index ixa_test__id1_x on test(id1, x);
    commit;
    --------------------------------------------------------------------------------

    set plan on;

    select *
    from test t
    where t.id1=1 and t.x>0
    ;
    --plan (t index (ixa_test__id1_x))
    --index ixa_test__id1_x is used

    --------------------------------------------------------------------------------

    select * from test t
    where t.id1=1 and t.x>0
    order by t.id1, t.id2, t.id3
    ;
    --plan (t order pk_test index (ixa_test__x))
    --index ixa_test__x - suboptimal
    --as you can see adding order by which consume some index (pk_test)
    --cause suboptimal choice of index (ixa_test__x)

    --------------------------------------------------------------------------------

    --if query is changed to order by not by index
    --plan sort (t index (ixa_test__id1_x))

    select * from test t
    where
        t.id1=1
        and t.x>0
    order by t.id1+0, t.id2, t.id3
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (T INDEX (IXA_TEST__ID1_X))
    PLAN SORT (T INDEX (IXA_TEST__ID1_X))
    PLAN SORT (T INDEX (IXA_TEST__ID1_X))
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
