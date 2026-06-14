#coding:utf-8

"""
ID:          issue-5933
ISSUE:       5933
TITLE:       Regression in 3.0+: message CTE 'X' has cyclic dependencies appear when 'X' is alias for resultset and there is previous CTE part with the same name 'X' in the query
DESCRIPTION:
JIRA:        CORE-5667
NOTES:
    [14.06.2026] pzotov
    1. Removed two examples that were taken from CORE-5655: could not reproduce problem described
       in this ticket on 3.0.3.32827-b0bef8f (04-nov-2017), i.e. on closest snapshot. 
    2. Replace RDB$DATABASE with regular custom table which has one record with always predictable
       value: on 6.x we have to avoid referring of RDB$DATABASE.RDB$RELATION_ID because GENERATOR
       is used to store generated relation_id instead of this field, see #bb280120.
    Confirmed problem that can be illustrated by remaining examples on 3.0.3.32827-b0bef8f.
    Checked on 6.0.0.2002; 5.0.5.1826; 4.0.8.3279; 3.0.14.33855
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table test(id int);
    insert into test(id) values(128);
    commit;

    with
    x as(
      select 1 i from test
    )
    ,y as(
      select i from x
    )
    select * from y as x ------------------ NOTE: "as X", i.e. alias for final CTE part ( "y" ) matches to 1st CTE ( "x" )
    ;

    -- Additional sample:
    with recursive
    a as(
      select 0 a from test
      UNION ALL
      select a+1 from a where a.a < 1
    )
    ,b as(
      select a b from a b
    )
    ,c as(
      select b c from b c
    )
    select c a from c a
    ;

    -- Two samples from CORE-5655:
    /*
    with cte as (
        select sign(t.id) u from test t
    )
    select u.u
    from cte u
    ;

    select e.v
    from (
        select d.v
        from (
            select sign(t.id) v from test t
        ) d
    ) e;
    */


"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    I 1
    A 0
    A 1
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
