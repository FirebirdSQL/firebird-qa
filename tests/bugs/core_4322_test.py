#coding:utf-8
#
# id:           bugs.core_4322
# title:        Engine crashes when use aggregate or window functions in recursive query (instead of producing compiling error)
# decription:   
# tracker_id:   CORE-4322
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='NONE', sql_dialect=3, init=init_script_1)

test_script_1 = """
with recursive
r as(
  select 0 i,count(*)over() c
  from rdb$database
  union all
  select r.i+1,sum(i)over() from r where r.i<10
)
select * from r; 

with recursive
r as(
  select 0 i,count(*) c from rdb$database
  union all
  select r.i + 1, 0 from r where sum(r.i) = 0
)
select * from r; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -104
-Recursive member of CTE cannot use aggregate or window function
Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -104
-Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

