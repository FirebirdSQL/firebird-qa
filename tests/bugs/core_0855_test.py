#coding:utf-8
#
# id:           bugs.core_0855
# title:        Aggregates in the WHERE clause vs derived tables
# decription:   Aggregates in the WHERE clause vs derived tables
# tracker_id:   CORE-855
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_855-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from (
  select rdb$relation_id
  from rdb$database
)
where sum(rdb$relation_id) = 0;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -104
-Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

