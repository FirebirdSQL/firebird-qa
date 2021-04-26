#coding:utf-8
#
# id:           functional.tabloid.dbp_1940_20110725_1159
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

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='tabloid-dbp-1940.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    with
    a as (
        select
            sum( max(t1.bv) )over(partition by t1.vi) sv
            ,max(t1.tm)over(partition by t1.vi) mt
            ,sum(coalesce(t2.bv, 0)) + max(t1.bv) rt
            ,t1.vi
            ,t1.tm
        from bbb t1
        left join bbb t2
        on t2.vi = t1.vi and t2.tm < t1.tm
        group by t1.vi,t1.tm
    )
    ,b as(
        select
            iif( t.sv = 255, min(t.mt)over(partition by iif(t.sv = 255,1,null)), null) as mt
            ,t.sv
            ,t.tm
            ,t.vi
            ,t.rt
        from a t
    )
    ,c as (
        select
            min(t.mt)over() mt
            ,t.tm
            ,t.vi
            ,t.rt
        from b t
    )
    ,d as (
        select
            t.vi,
            dateadd(t2.rn second to t.mt) xdt,
            max(iif(t.tm > dateadd(t2.rn second to t.mt) and t.tm >= dateadd(t2.rn second to t.mt), 0, t.rt) ) rt
        from c t
        cross join (
            select t.rn
            from (select row_number()over(order by (tm))-1 rn from bbb) t
            where t.rn < 30
        ) t2
        group by 1,2
    )
    select t.xdt f01, count(*) f02
    from d t
    where t.rt >= 255. / 3. and t.rt <= ( 255. / 3. ) * 2.
    group by 1
    order by 1,2
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F01                             2003-01-01 01:11:00.0000
    F02                             1
    F01                             2003-01-01 01:11:01.0000
    F02                             3
    F01                             2003-01-01 01:11:02.0000
    F02                             4
    F01                             2003-01-01 01:11:03.0000
    F02                             4
    F01                             2003-01-01 01:11:04.0000
    F02                             3
    F01                             2003-01-01 01:11:05.0000
    F02                             3
    F01                             2003-01-01 01:11:06.0000
    F02                             3
    F01                             2003-01-01 01:11:07.0000
    F02                             3
    F01                             2003-01-01 01:11:08.0000
    F02                             3
    F01                             2003-01-01 01:11:09.0000
    F02                             3
    F01                             2003-01-01 01:11:10.0000
    F02                             4
    F01                             2003-01-01 01:11:11.0000
    F02                             5
    F01                             2003-01-01 01:11:12.0000
    F02                             4
    F01                             2003-01-01 01:11:13.0000
    F02                             4
    F01                             2003-01-01 01:11:14.0000
    F02                             3
    F01                             2003-01-01 01:11:15.0000
    F02                             3
    F01                             2003-01-01 01:11:16.0000
    F02                             3
    F01                             2003-01-01 01:11:17.0000
    F02                             4
    F01                             2003-01-01 01:11:18.0000
    F02                             4
    F01                             2003-01-01 01:11:19.0000
    F02                             4
    F01                             2003-01-01 01:11:20.0000
    F02                             4
    F01                             2003-01-01 01:11:21.0000
    F02                             4
    F01                             2003-01-01 01:11:22.0000
    F02                             4
    F01                             2003-01-01 01:11:23.0000
    F02                             4
    F01                             2003-01-01 01:11:24.0000
    F02                             4
    F01                             2003-01-01 01:11:25.0000
    F02                             4
    F01                             2003-01-01 01:11:26.0000
    F02                             4
    F01                             2003-01-01 01:11:27.0000
    F02                             4
    F01                             2003-01-01 01:11:28.0000
    F02                             4
    F01                             2003-01-01 01:11:29.0000
    F02                             4
  """

@pytest.mark.version('>=3.0')
def test_dbp_1940_20110725_1159_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

