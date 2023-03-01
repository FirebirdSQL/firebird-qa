#coding:utf-8

"""
ID:          issue-3357
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/3357
TITLE:       Bad execution plan if some stream depends on multiple streams via a function [CORE2975]
NOTES:
    [01.03.2023] pzotov
    ::: NB :::
    Plan that was described in the ticked as expected (see starting issue, dated in 2010) currently
    can be seen only fin FB 3.x and 4.x.
    As of FB 5.x, its plan contains two-step HASH  JOIN.

    Checked on 3.0.11.33665, 4.0.3.2904, 5.0.0.964
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table T1 (ID int, COL int);
    create index T1_ID on T1 (ID);
    create unique index T1_COL on T1 (COL);

    create table T2 (ID int);
    create index T2_ID on T2 (ID);

    create table T3 (ID int);
    create index T3_ID on T3 (ID);

    set plan;
    select *
    from T1
    join T2 on T2.ID = T1.ID
    join T3 on T3.ID = coalesce(T1.ID, T2.ID)
    where T1.COL = 1;
"""

act = isql_act('db', test_script)

fb4x_expected_stdout = """
    PLAN JOIN (T1 INDEX (T1_COL), T2 INDEX (T2_ID), T3 INDEX (T3_ID))
"""

fb5x_expected_stdout = """
    PLAN HASH (HASH (T1 INDEX (T1_COL), T2 NATURAL), T3 NATURAL)
"""

@pytest.mark.version('>=3.0.9')
def test_1(act: Action):
    act.expected_stdout = fb4x_expected_stdout if act.is_version('<5') else fb5x_expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
