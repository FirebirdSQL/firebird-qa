#coding:utf-8
#
# id:           bugs.core_5957
# title:        Bug in SIMILAR TO when adding numeric quantifier as bound for repetetion of expression leads to empty resultset
# decription:   
#                
# tracker_id:   CORE-5957
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    set count on;
    select 1 from rdb$database where 'SLEEP' similar to '(DELAY|SLEEP|PAUSE){1}'; -- 2.5 fails here
    select 2 from rdb$database where 'SLEEP' similar to '(DELAY|SLEEP|PAUSE){1,}';  -- 2.5 fails here
    select 3 from rdb$database where 'SLEEP' similar to '(DELAY|SLEEP|PAUSE)+'; 
    select 4 from rdb$database where 'SLEEP' similar to '(DELAY|SLEEP|PAUSE)*'; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1
    Records affected: 1

    2
    Records affected: 1

    3
    Records affected: 1

    4
    Records affected: 1

  """

@pytest.mark.version('>=3.0')
def test_core_5957_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

