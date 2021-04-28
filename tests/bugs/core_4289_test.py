#coding:utf-8
#
# id:           bugs.core_4289
# title:        Regression: NOT-null field from derived table became NULL when is referred outside DT
# decription:   
# tracker_id:   CORE-4289
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
set list on;
select q.n, case when q.n=0 then 'zero' when q.n<>0 then 'NON-zero' else 'Hm!..' end what_is_n
from (select 0 N from RDB$DATABASE) q; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
N                               0
WHAT_IS_N                       zero    
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

