#coding:utf-8
#
# id:           bugs.core_3546
# title:        Aliases for the RETURNING clause
# decription:   
# tracker_id:   CORE-3546
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t(id int, x int default 123, y int default 456);
    commit;
    set list on;
    insert into t(id) values(1) returning x+y as i234567890123456789012345678901;
    insert into t(id) values(2) returning x-y    "/** That's result of (x-y) **/";
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    I234567890123456789012345678901 579
    /** That's result of (x-y) **/  -333
  """

@pytest.mark.version('>=3.0')
def test_core_3546_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

