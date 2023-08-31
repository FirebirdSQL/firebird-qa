#coding:utf-8

"""
ID:          issue-7727
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7727
TITLE:       Index for integer column cannot be used when INT128/DECFLOAT value is being searched
DESCRIPTION:
NOTES:
    [31.08.2023] pzotov
    Confirmed problem on 5.0.0.1177, 4.0.4.2979
    Checked on 5.0.0.1183, 4.0.4.2983 (intermediate snapshots).
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = f"""
    recreate table test_a (
        id bigint not null,
        constraint pk_test primary key(id)
    );

    recreate table test_b (
        id bigint not null,
        constraint pk_test_b primary key(id)
    );


    set plan on;

    select ta.id, tb.id
    from test_a ta
    left join test_b tb on tb.id = ta.id / cast(1000 as int128);

    select ta.id, tb.id
    from test_a ta
    left join test_b tb on tb.id = ta.id / cast(1000 as decfloat);
"""

act = isql_act('db', test_script)

expected_stdout = f"""
    PLAN JOIN (TA NATURAL, TB INDEX (PK_TEST_B))
    PLAN JOIN (TA NATURAL, TB INDEX (PK_TEST_B))
"""

@pytest.mark.version('>=4.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
