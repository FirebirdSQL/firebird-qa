#coding:utf-8
#
# id:           functional.tabloid.dbp_5125_windowed_funcs
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

db_1 = db_factory(from_backup='tabloid-dbp-5125.fbk', init=init_script_1)

test_script_1 = """
    with
    cx as(
        select ari, tbi,
            dense_rank() over(partition by ari order by dts) ra,
            dense_rank() over(partition by ari order by dts desc)rd
            from pdata
    )
    ,dx as (
        select ari, tbi, dts
        ,min(dts)over(partition by ari) dts_min
        ,max(dts)over(partition by ari) dts_max
        from pdata
    )
    
    select
        c1.tbi vx
        ,c1.ari q1
        ,c2.ari q2
    from cx  c1
    join cx c2 on
        c1.ari<>c2.ari
        and c1.tbi=c2.tbi
        and c1.ra=c2.rd
        and c1.ra=1
    
    full join (
        select a.tbi as vx, a.ari as q1, b.ari as q2
        from dx a, dx b
        where a.dts_min = a.dts and b.dts_max=b.dts and a.ari<>b.ari and a.tbi=b.tbi
    ) d
    on c1.tbi = d.vx and c1.ari=d.q1 and c2.ari=d.q2
    order by 1,2,3
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          VX           Q1           Q2 
          26           10            9 
          39           14           13 
          42           16           15 
          44           17           19 
          45           18           17 
          45           20           17 
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

