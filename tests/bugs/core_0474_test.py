#coding:utf-8
#
# id:           bugs.core_0474
# title:        Redundant evaluations in COALESCE
# decription:   
#                  Proper result - only since 2.5.0 :-)
#                  On WI-V2.1.7.18553 Firebird 2.1 result still wrong (curr_gen 4)
#                
# tracker_id:   CORE-0474
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create generator g1;
    commit;
    set list on;
    select 
        coalesce( 
                   nullif(gen_id(g1,1),1), 
                   nullif(gen_id(g1,1),2), 
                   gen_id(g1,1), 
                   nullif(gen_id(g1,1),4), 
                   gen_id(g1,1) 
                ) 
                as curr_gen 
    from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CURR_GEN                        3
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

