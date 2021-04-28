#coding:utf-8
#
# id:           bugs.core_0148
# title:        SELECT '1' UNION SELECT '12'
# decription:   
# tracker_id:   CORE-0148
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
    -- Confirmed: runtime error on WI-V1.5.6.5026:
    -- -SQL error code = -104
    -- -Invalid command
    -- -Data type unknown

    recreate table test_a(x int);
    recreate table test_b(y int);

    insert into test_a values(9999999);
    insert into test_b values(888888);

    set list on;
    select '1' || a.x as result
    from test_a a
    union
    select '12' || b.y
    from test_b b
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          12888888
    RESULT                          19999999
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

