#coding:utf-8
#
# id:           bugs.core_5667
# title:        Regression in 3.0+: message CTE 'X' has cyclic dependencies appear when 'X' is alias for resultset and there is previous CTE part with the same name 'X' in the query
# decription:   
#                   Checked on:
#                       25SC, build 2.5.8.27088: OK, 0.344s.
#                       30SS, build 3.0.3.32856: OK, 0.968s.
#                       40SS, build 4.0.0.834: OK, 1.875s.
#                
# tracker_id:   CORE-5667
# min_versions: ['2.5.8']
# versions:     2.5.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with
    x as(
      select 1 i from rdb$database
    )
    ,y as(
      select i from x
    )
    select * from y as x ------------------ NOTE: "as X", i.e. alias for final CTE part ( "y" ) matches to 1st CTE ( "x" )
    ; 

    -- Additional sample:
    with recursive
    a as(
      select 0 a from rdb$database
      union all
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
    with cte as (select sign(t.rdb$relation_id) ct from rdb$database t) select ct.ct from cte ct;
    select e.ct from (select d.ct from (select sign(t.rdb$relation_id) ct from rdb$database t) d) e;


  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    I                               1

    A                               0
    A                               1

    CT                              1
    CT                              1
  """

@pytest.mark.version('>=2.5.8')
def test_core_5667_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

