#coding:utf-8
#
# id:           bugs.core_6421
# title:        Parameter in offset expression in LAG, LEAD, NTH_VALUE window functions requires explicit cast to BIGINT or INTEGER
# decription:   
#                   Confirmed bug on 4.0.0.2225, got: SQLSTATE = HY004 / Dynamic SQL Error / -SQL error code = -804 / -Data type unknown
#                   Checked on intermediate build 4.0.0.2235 (timestamp: 26.10.2020 01:19): all fine.
#                
# tracker_id:   CORE-6421
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('PLAN .*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;

    select rdb$relation_name, lag(rdb$relation_name, ?) over (order by rdb$relation_name) from rdb$relations;
    select rdb$relation_name, lead(rdb$relation_name, ?) over (order by rdb$relation_name) from rdb$relations;
    select rdb$relation_name, nth_value(rdb$relation_name, ?) over (order by rdb$relation_name) from rdb$relations;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()

