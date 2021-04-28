#coding:utf-8
#
# id:           bugs.core_6355
# title:        TRUNC() does not accept second argument = -128 (but shows it as required boundary in error message)
# decription:   
#                   Checked on 4.0.0.2091 - all OK.
#                   (intermediate snapshot with timestamp: 08.07.20 15:10)
#                
# tracker_id:   CORE-6355
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select trunc(0,-128) from rdb$database; 
    select trunc(9223372036854775807,-128) from rdb$database; 
    select trunc(170141183460469231731687303715884105727,-128) from rdb$database; 
    select trunc(-9223372036854775808,-128) from rdb$database; 
    select trunc(-170141183460469231731687303715884105728,-128) from rdb$database; 

    -- (optional) check upper bound (127):
    select trunc(0,127) from rdb$database; 
    select trunc(9223372036854775807,127) from rdb$database; 
    select trunc(170141183460469231731687303715884105727,127) from rdb$database; 
    select trunc(-9223372036854775808,127) from rdb$database; 
    select trunc(-170141183460469231731687303715884105728,127) from rdb$database; 

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    0
    0
    0
    0
    0
    0
    9223372036854775807
    170141183460469231731687303715884105727
    -9223372036854775808
    -170141183460469231731687303715884105728
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

