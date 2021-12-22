#coding:utf-8
#
# id:           bugs.core_2974
# title:        Unexpected "Invalid SIMILAR TO pattern" error
# decription:   
#                
# tracker_id:   CORE-2974
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    -- Should raise "Invalid SIMILAR TO pattern" error, as minus sign should be ecaped 
    select case when '-1' similar to '(-)%' then 1 else 0 end as chk_a
      from rdb$database 
    ;

    -- Should raise "Invalid SIMILAR TO pattern" error because there is no "default" escape character:
    select case when '-1' similar to '(\\-)%' then 1 else 0 end as chk_b
      from rdb$database 
    ;

    -- Should NOT raise error:
    select case when '-1' similar to '(\\-)%' escape '\\' then 1 else 0 end as chk_c
      from rdb$database 
    ;
    -- works ok 

    -- Should NOT raise error:
    select case when '-1' similar to '(\\+)%' then 1 else 0 end as chk_d
      from rdb$database 
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHK_C                           1
    CHK_D                           0
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Invalid SIMILAR TO pattern

    Statement failed, SQLSTATE = 42000
    Invalid SIMILAR TO pattern
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

