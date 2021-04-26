#coding:utf-8
#
# id:           bugs.core_0211
# title:        SELECT...HAVING...NOT IN crashes server
# decription:   
#                  Crashed on: WI-V3.0.0.32380, WI-T4.0.0.32399, found 16-mar-2016.
#                  Passed on:  WI-V3.0.0.32487, WI-T4.0.0.141 -- works fine.
#                
# tracker_id:   CORE-0211
# min_versions: ['2.0']
# versions:     2.0.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.0
# resources: None

substitutions_1 = [('RDB\\$RELATION_ID[ ]+\\d+', 'RDB$RELATION_ID')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select r.rdb$relation_id, count(*)
    from rdb$database r
    group by r.rdb$relation_id
    having count(*) not in (select r2.rdb$relation_id from rdb$database r2);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$RELATION_ID                 134
    COUNT                           1
  """

@pytest.mark.version('>=2.0.0')
def test_core_0211_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

