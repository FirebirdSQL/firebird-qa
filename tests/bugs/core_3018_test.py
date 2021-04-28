#coding:utf-8
#
# id:           bugs.core_3018
# title:        Check ability to use RECREATE, ALTER and CREATE OR ALTER SEQUENCE/GENERATOR statements
# decription:   
#                   NOTE: FB 4.x has incompatible behaviour with all previous versions since build 4.0.0.2131 (06-aug-2020):
#                   statement 'alter sequence <seq_name> restart with 0' changes rdb$generators.rdb$initial_value to -1 thus
#                   next call of gen_id(<seq_name>,1) will return 0 (ZERO!) rather than 1. 
#                   See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d
#                   This is considered as *expected* and is noted in doc/README.incompatibilities.3to4.txt
#               
#                   For this reason, old code was removed and now test checks only ability to use statements rather than results of them.
#                   Checked on: 4.0.0.2119; 4.0.0.2164; 3.0.7.33356.
#                 
# tracker_id:   CORE-3018
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('end of command.*', 'end of command')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Only FIRST of following statements must fail with 
    -- SQLSTATE = 42000 / Dynamic SQL Error / -SQL error code = -104 / -Unexpected end of command.
    -- All subsequent must pass w/o errors.
    create or alter sequence g01;
    
    create or alter sequence g02 start with 2;
    
    create or alter sequence g03 start with 2 increment by 3;
    
    create or alter sequence g04 restart increment by 4;

    --#####################################################

    recreate sequence g05;
    
    recreate sequence g06 start with 6;
    
    recreate sequence g07 start with 7 increment by 8;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Unexpected end of command
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

