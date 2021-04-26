#coding:utf-8
#
# id:           bugs.core_5153
# title:        Regression: Server crashes when aggregate functions are used together with NOT IN predicate
# decription:   
#                  ::: NB :::
#                  Here we only check that server is alive after running query but WITHOUT checking its data
#                  (see: "and 1=0" below in HAVING section).
#                  We do NOT check correctness of query results - this will be done by another ticket, CORE-5165: 
#                  wrong result in 3.0 RC2 and 4.0 comparing 2.5. It's NOT related to this ticket.
#               
#                  Confirmed success (no crash) on snapshots 3.0 RC2 and 4.0 with timestamp 23-mar-2016.
#                  Crash was detected on WI-V3.0.0.32378.
#                
# tracker_id:   CORE-5153
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    select r.rdb$relation_id as id, count(*) as cnt
    from rdb$database r
    group by r.rdb$relation_id
    having count(*) not in (select r2.rdb$relation_id from rdb$database r2)
    and 1=0
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_5153_1(act_1: Action):
    act_1.execute()

