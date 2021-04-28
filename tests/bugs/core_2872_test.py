#coding:utf-8
#
# id:           bugs.core_2872
# title:        EVL_expr: invalid operation (232)
# decription:   
#                   Confirmed on WI-V2.5.0.26074 and 2.5.7.27027, got:
#                   ===
#                     Statement failed, SQLSTATE = XX000
#                     internal Firebird consistency check (EVL_expr: invalid operation (232), file: evl.cpp line: 1207)
#                     After line 2 in file c2872.sql
#                     Statement failed, SQLSTATE = XX000
#                     internal Firebird consistency check (can't continue after bugcheck)
#                   ===
#                
# tracker_id:   CORE-2872
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
    set list on;
    set count on;
    select 1 as i 
    from rdb$database
    where count(*) >= all (select count(*) from rdb$database)
    ;
    select 1 as k 
    from rdb$database
    where count(*) = (select count(*) from rdb$database)
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

