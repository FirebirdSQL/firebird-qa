#coding:utf-8
#
# id:           bugs.core_1793
# title:        AV at prepare of query with unused parametrized CTE
# decription:   
# tracker_id:   CORE-1793
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1793

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Updated 06.01.2018:
    --  25SC, build 2.5.8.27089: OK, 0.297s.
    --  30SS, build 3.0.3.32861: OK, 1.578s.
    --  40SS, build 4.0.0.840: OK, 1.390s.
    recreate table test(x int);
    commit;
    set planonly;
    with
        x as (select x.x from test x),
        y as (select y.x from test y)
    select * from y;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (Y Y NATURAL)
  """
expected_stderr_1 = """
    SQL warning code = -104
    -CTE "X" is not used in query
  """

@pytest.mark.version('>=2.5')
def test_core_1793_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

