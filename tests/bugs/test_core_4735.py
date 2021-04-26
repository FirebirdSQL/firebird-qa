#coding:utf-8
#
# id:           bugs.core_4735
# title:        Expression 'where bool_field IS true | false' should also use index as 'where bool_field = true | false' (if such index exists)
# decription:   
#                   Changed expected PLAN of execution after dimitr's letter 28.01.2019 17:28: 
#                   'is NOT <bool>' and 'is distinct from <bool>' should use  PLAN NATURAL.
#                
# tracker_id:   CORE-4735
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
    recreate table test(x boolean, unique(x) using index test_x);
    commit;

    set plan on;
    select 1 from test where x = true ;
    select 1 from test where x is true ;
    select 0 from test where x = false ;
    select 0 from test where x is false ;
    select 1 from test where x is not true ; -- this must have plan NATURAL, 26.01.2019
    select 1 from test where x is distinct from true ; -- this must have plan NATURAL, 26.01.2019
    select 1 from test where x is not false ; -- this must have plan NATURAL, 26.01.2019
    select 1 from test where x is distinct from false ; -- this must have plan NATURAL, 26.01.2019
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST INDEX (TEST_X))
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
    PLAN (TEST NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_core_4735_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

