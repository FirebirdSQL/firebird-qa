#coding:utf-8
#
# id:           bugs.core_4572
# title:        Regression: Incorrect result in subquery with aggregate
# decription:   
# tracker_id:   CORE-4572
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
    set term ^;
    create or alter function fn_multiplier ( a_val int, a_times int ) returns bigint
    as
    begin
        return a_val * a_times;
    end
    ^
     
    create or alter procedure sp_multiplier (a_val int, a_times int )
    returns (result bigint)
    as
    begin
        result = a_val * a_times;
    end
    ^
    set term ;^
    commit;
    
    -- Confirmed on WI-T3.0.0.31374 Firebird 3.0 Beta 1:
    -- Statement failed, SQLSTATE = 39000
    -- invalid request BLR at offset 50
    -- -function FN_MULTIPLIER could not be matched
    select fn_multiplier(191) as t from rdb$database;

    execute procedure sp_multiplier(191);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 07001
    Dynamic SQL Error
    -Input parameter mismatch for function FN_MULTIPLIER

    Statement failed, SQLSTATE = 07001
    Dynamic SQL Error
    -Input parameter mismatch for procedure SP_MULTIPLIER
  """

@pytest.mark.version('>=3.0')
def test_core_4572_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

