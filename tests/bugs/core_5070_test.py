#coding:utf-8

"""
ID:          issue-5357
ISSUE:       5357
TITLE:       Compound index cannot be used for filtering in some ORDER/GROUP BY queries
DESCRIPTION:
JIRA:        CORE-5070
FBTEST:      bugs.core_5070
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test1 (
        ia integer not null,
        id integer not null,
        it integer not null,
        dt date not null,
        constraint test1_pk_ia_id primary key (ia,id)
    );

    set plan on;
    set explain on;

    select *
    from test1
    where
        ia=1 and dt='01/01/2015' and it=1
    order by id
    ;


    select id
    from test1
    where
        ia=1 and dt='01/01/2015' and it=1
    group by id
    ;

"""

act = isql_act('db', test_script)

expected_stdout = """
    Select Expression
        -> Filter
            -> Table "TEST1" Access By ID
                -> Index "TEST1_PK_IA_ID" Range Scan (partial match: 1/2)

    Select Expression
        -> Aggregate
            -> Filter
                -> Table "TEST1" Access By ID
                    -> Index "TEST1_PK_IA_ID" Range Scan (partial match: 1/2)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
