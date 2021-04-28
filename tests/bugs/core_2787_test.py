#coding:utf-8
#
# id:           bugs.core_2787
# title:        Make rdb$system_flag not null
# decription:   
# tracker_id:   CORE-2787
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set count on;
    set list on;

    select rf.rdb$relation_name as rel_name, rf.rdb$null_flag as nullable
    from rdb$relation_fields rf
    where 
        upper(rf.rdb$field_name) = upper('rdb$system_flag')
        and rdb$null_flag = 1;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

