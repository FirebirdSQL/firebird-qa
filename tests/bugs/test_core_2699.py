#coding:utf-8
#
# id:           bugs.core_2699
# title:        Common table expression context could be used with parameters
# decription:   
# tracker_id:   CORE-2699
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At line.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    with x as (
        select 1 n from rdb$database
    )
    select * from x(10);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -204
    -Procedure unknown
    -X
    -At line 4, column 15
  """

@pytest.mark.version('>=3.0')
def test_core_2699_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

