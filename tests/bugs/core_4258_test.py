#coding:utf-8
#
# id:           bugs.core_4258
# title:        Regression: Wrong boundary for minimum value for BIGINT/DECIMAL(18)
# decription:   
# tracker_id:   CORE-4258
# min_versions: ['2.1']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(x decimal(18), y bigint);
    commit;
    insert into test values( -9223372036854775808, -9223372036854775808);
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select * from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               -9223372036854775808
    Y                               -9223372036854775808
  """

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

