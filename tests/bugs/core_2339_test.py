#coding:utf-8
#
# id:           bugs.core_2339
# title:        Incorrect result for the derived expression based on aggregate and computation
# decription:   
#                27.07.2021: changed output form using SET LIST ON, added subst. to remove dependency on the number of inner spaces.
#                Checked on:
#                   5.0.0.113 SS: 1.025s.
#                   5.0.0.88 SS: 1.028s.
#                   4.0.1.2539 SS: 0.942s.
#                   3.0.8.33476 SS: 2.076s.
#                   2.5.9.27152 SC: 0.170s.
#                
# tracker_id:   CORE-2339
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select * from ( select sum(1)*1 as "sum_1_multiplied_for_1" from rdb$database );
    -- result is NULL instead of 1
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    sum_1_multiplied_for_1 1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

