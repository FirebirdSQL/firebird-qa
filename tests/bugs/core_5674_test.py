#coding:utf-8
#
# id:           bugs.core_5674
# title:        Allow unused Common Table Expressions
# decription:   
#                   Checked on:
#                       3.0.3.32852: OK, 0.875s.
#                       4.0.0.830: OK, 1.062s.
#                
# tracker_id:   CORE-5674
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '-At line: column:')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    -- Should PASS but two warnings will be issued:
    -- SQL warning code = -104
    -- -CTE "X" is not used in query
    -- -CTE "Y" is not used in query
    with
    x as(
      select 1 i from rdb$database
    )
    ,y as(
      select i from x
    )
    ,z as (
      select 2 z from rdb$database
    )
    select z y, z*2 x from z
    ; 


    -- Should PASS but one warning will be issued:
    -- SQL warning code = -104
    -- -CTE "B" is not used in query
    with
    a as(
      select 0 a from rdb$database
    )
    ,b as(
      select 1 x from c rows 1
    )
    ,c as(
      select 2 x from d rows 1
    )
    ,d as(
      select 3 x from e rows 1
    )
    ,e as(
      select a x from a rows 1
    )
    select * from e
    -- union all select * from b
    ;


    -- Should FAIL with:
    -- Statement failed, SQLSTATE = 42S02
    -- Dynamic SQL Error
    -- -SQL error code = -204
    -- -Table unknown
    -- -FOO
    with recursive
    a as(
      select 0 a from rdb$database
      union all
      select a+1 from a where a.a < 1
    )
    ,b as(
      select 1 a from foo rows 1
    )
    ,c as(
      select 2 b from bar rows 1
    )
    select * from a;

    -- Should FAIL with:
    -- Statement failed, SQLSTATE = 42000
    -- Dynamic SQL Error
    -- -SQL error code = -104
    -- -CTE 'C' has cyclic dependencies
    with recursive
    a as(
      select 0 a from rdb$database
      union all
      select a+1 from a where a.a < 1
    )
    ,b as(
      select 1 a from c rows 1
    )
    ,c as(
      select 2 b from b rows 1
    )
    select * from a;


"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Y                               2
    X                               4

    X                               0
"""
expected_stderr_1 = """
    SQL warning code = -104
    -CTE "X" is not used in query
    -CTE "Y" is not used in query

    SQL warning code = -104
    -CTE "B" is not used in query
    -CTE "C" is not used in query
    -CTE "D" is not used in query
    
    Statement failed, SQLSTATE = 42S02
    Dynamic SQL Error
    -SQL error code = -204
    -Table unknown
    -FOO
    -At line: column:

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -CTE 'C' has cyclic dependencies
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

