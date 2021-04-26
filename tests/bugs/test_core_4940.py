#coding:utf-8
#
# id:           bugs.core_4940
# title:        Add label about deterministic flag for stored function in SHOW and extract commands
# decription:   
# tracker_id:   CORE-4940
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!Deterministic|deterministic).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 1. Specify 'deterministic' flag - it should be reflected in SHOW command:
    set term ^;
    create or alter function fn_infinity returns bigint deterministic as
    begin
        return 9223372036854775807;
    end
    ^
    set term ;^
    commit;
    
    show function fn_infinity;
    
    -- 2. Remove 'deterministic' flag - it also should be reflected in SHOW command:
    set term ^;
    alter function fn_infinity returns bigint as
    begin
        return 9223372036854775807;
    end
    ^
    set term ;^
    commit;
    
    show function fn_infinity;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Deterministic function
  """

@pytest.mark.version('>=3.0')
def test_core_4940_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

