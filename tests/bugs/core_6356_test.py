#coding:utf-8
#
# id:           bugs.core_6356
# title:        ROUND() does not allow second argument >=1 when its first argument is more than MAX_BIGINT / 10
# decription:   
#                   Checked on 4.0.0.2091 - all OK.
#                   (intermediate snapshot with timestamp: 08.07.20 15:10)
#                
# tracker_id:   CORE-6356
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
    select round( 9223372036854775807, 1) from rdb$database; 
    select round( 170141183460469231731687303715884105727, 1) from rdb$database; 


    select round( -9223372036854775808, 1) from rdb$database; 
    select round( -170141183460469231731687303715884105728, 1) from rdb$database; 

    select round( 9223372036854775807, 127) from rdb$database; 
    select round( 170141183460469231731687303715884105727, 127) from rdb$database; 

    select round( -9223372036854775808, -128) from rdb$database; 
    select round( -170141183460469231731687303715884105728, -128) from rdb$database; 

    select round( -9223372036854775808, 127) from rdb$database; 
    select round( -170141183460469231731687303715884105728, 127) from rdb$database; 

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    9223372036854775807
    170141183460469231731687303715884105727
    -9223372036854775808
    -170141183460469231731687303715884105728
    9223372036854775807
    170141183460469231731687303715884105727
    0
    0
    -9223372036854775808
    -170141183460469231731687303715884105728
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

