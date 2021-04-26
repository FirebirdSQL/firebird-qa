#coding:utf-8
#
# id:           functional.tabloid.dbp_4391_combo_full_join_and_windowed_funcs2
# title:        Common SQL. Check correctness of the results
# decription:   
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(from_backup='tabloid-dbp-4391.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    with recursive
    nx as (select 0 x from rdb$database union all select r.x+1 from nx r where r.x<2)
    ,t as (
        select
            row_number()over(partition by d.ari order by d.dts, d.tbi) n,
            d.ari, d.tbi, t.tc c
        from pdata d cross join ptube t
        where d.tbi = t.id
    )
    ,z as(
        select
            t.ari
            ,max(iif(x=0, tbi, null)) v1
            ,max(iif(x=1, tbi, null)) v2
            ,max(iif(x=2, tbi, null)) v3
        from t cross join nx
        group by t.ari, t.n - x
        having
            max(iif(x=0, c, null) )='rio' and
            max(iif(x=1, c, null) )='foo' and
            max(iif(x=2, c, null) )='bar'
    )
    ,dx as
    (
        select ari,
            row_number()over(partition by ari order by dts, tbi ) as i,
            tc,
            tbi as bx
        from pdata join ptube on tbi = id
    )
    ,tx as
    (
        select
            ari,
            tc as c1,
            lead(tc)over(partition by ari order by i ) as c2,
            lead(tc,2)over(partition by ari order by i ) as c3,
            bx as v1  ,
            lead(bx)over(partition by ari order by i ) as v2,
            lead(bx,2)over(partition by ari order by i ) as v3
        from   dx
    )
    ,x as(
        select
            ari,
            v1,
            v2,
            v3
        from tx
        where c1 = 'rio'
          and c2 = 'foo'
          and c3 = 'bar'
    )
    select count(*) cnt
    from z full join x using(ari, v1, v2, v3)
    where
        x.ari is distinct from z.ari
        or x.v1 is distinct from z.v1
        or x.v2 is distinct from z.v2
        or x.v3 is distinct from z.v3
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             0
  """

@pytest.mark.version('>=3.0')
def test_dbp_4391_combo_full_join_and_windowed_funcs2_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

