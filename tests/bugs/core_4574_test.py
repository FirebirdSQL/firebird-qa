#coding:utf-8
#
# id:           bugs.core_4574
# title:        Regression: Incorrect result in subquery with aggregate
# decription:   
#                   30.10.2019. NB: new datatype in FB 4.0 was introduces: numeric(38,0).
#                   It can lead to additional ident of values when we show them in form "SET LIST ON",
#                   so we have to ignore all internal spaces - see added 'substitution' section below.
#                   Checked on:
#                       4.0.0.1635 SS: 1.197s.
#                       3.0.5.33182 SS: 0.848s.
#                       2.5.9.27146 SC: 0.188s.
#                
# tracker_id:   CORE-4574
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with
    a as (
        select 1 id from rdb$database
        union all
        select 2 from rdb$database
        union all
        select 3 from rdb$database
    ),
    b as (
        select 1 id1, null id2 from rdb$database
        union all
        select 2, null from rdb$database
        union all
        select 3, null from rdb$database
    )
    select
        sum((select count(*) from B where B.ID1 = A.ID)) s1
        ,sum((select count(*) from B where B.ID2 = A.ID)) s2
        -- must be (3,0) (FB2.5) , but not (3,3) (FB3.0)
    from a;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    S1                              3
    S2                              0
"""

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

