#coding:utf-8
#
# id:           functional.tabloid.bus_3103_windowed_funcs
# title:        Query for test MAX()OVER().
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

db_1 = db_factory(from_backup='tabloid-bus-3103.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    with
    dx as (
         select
            t.cid
            ,p.pid
            ,hash(src) + hash(tgt) sth
            ,datediff(minute from dts0 to dts1 + iif(t.dts1 < t.dts0, 1, 0)) dd
         from tmove t
            left join pmove p on t.id = p.tid
    )
    ,mx as (
        select
            dx.*,
            nullif( abs( max(dd)over() - max(dd)over(partition by cid, sth) ), 1) ns
         from dx
    )
    select
        (select name from clist c where c.id  = mx.cid) cnm,
        count(pid) cnt
    from   mx
    where  ns = 0
    group  by mx.cid
    having count(pid) > 0;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNM                             ba        
    CNT                             13
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

