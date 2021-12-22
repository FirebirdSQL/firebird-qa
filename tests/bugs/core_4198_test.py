#coding:utf-8
#
# id:           bugs.core_4198
# title:         Incorrect "token unknown" error when the SQL string ends with a hex number literal
# decription:   
# tracker_id:   CORE-4198
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; 
    select 1 v_passed from rdb$database where 1 = 0x1 ;
    select 2 v_failed from rdb$database where 1 = 0x1; -- confirmed fail on 3.0 Alpha1 (passes OK on Alpha2)
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    V_PASSED                        1
    V_FAILED                        2
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

