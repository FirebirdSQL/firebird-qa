#coding:utf-8
#
# id:           functional.tabloid.dbp_2146_distinct_not_in
# title:        Common SQL. Check correctness of the results
# decription:   
# tracker_id:   
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(from_backup='tabloid-dbp-2146.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    with
    eset
    as(
    select tbi, count(distinct ari) as cnt
    from pdata u
    where (
            select count(distinct ari)
            from pdata where tbi=u.tbi
          ) > 2
    group by tbi having sum(cv)=16*16-1
    )
    ,wset
    as(
        select ari
        from pdata 
        where tbi in (
            select tbi from pdata group by tbi
            having sum(cv)=16*16-1
        )
        group by ari having sum(cv)=1000-235
    )
    ,q1 as(
        select distinct pa.id ari, pt.id tbi, p.cnt
        from pdata u
        join eset p on p.tbi=u.tbi
        join parea pa on pa.id=u.ari
        join ptube pt on pt.id=u.tbi
        join wset b on b.ari=u.ari
    )
    ,q2 as (
        select 
            a.ari
            ,a.tbi
            ,b.cnt
        from
        (
            select distinct a.ari, b.tbi
            from
            (
                select ari
                from pdata 
                where tbi not in (
                    select tbi
                    from pdata
                    group by tbi
                    having sum(cv) <> 16*16-1
                )
                group by ari
                having 1000 - sum(cv) =  235
            ) a
            , pdata b
            where a.ari = b.ari
        ) a,
        (
            select tbi, count(distinct ari) cnt
            from pdata group by tbi
            having count(distinct ari) > 2
        ) b
        where a.tbi = b.tbi
    )
    select ari,tbi,cnt
    from q1 natural join q2
    order by 1,2,3
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ARI                             6
    TBI                             10
    CNT                             3  
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

