#coding:utf-8
#
# id:           bugs.core_4173
# title:        Setting generator value twice in single transaction will set it to zero
# decription:   
# tracker_id:   CORE-4173
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off;
    set list on;
    create generator g;
    commit;
    set generator g to 111;
    commit;
    select gen_id(g,0) value_on_step_1 from rdb$database;
    set generator g to 222;
    set generator g to 333;
    select gen_id(g,0) value_on_step_2 from rdb$database;
    commit;
    select gen_id(g,0) value_on_step_3 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    VALUE_ON_STEP_1                 111
    VALUE_ON_STEP_2                 333
    VALUE_ON_STEP_3                 333
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

