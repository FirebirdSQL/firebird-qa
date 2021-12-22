#coding:utf-8
#
# id:           bugs.core_3423
# title:        [FB3] Wrong RDB$PARAMETER_MECHANISM
# decription:   
# tracker_id:   CORE-3423
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure sp_test(IN_ARG INTEGER) returns (OUT_ARG INTEGER) as
    begin
        OUT_ARG=IN_ARG;
    end
    ^
    set term ;^
    commit;
    
    set list on;
    -- NB: engine treats nulls and zeroes as the same value, so it is enough to check that
    -- parameter mechanism is either null or zero only:
    select 
      pp.rdb$parameter_name p_name
     ,iif( coalesce(pp.rdb$parameter_mechanism,0) = 0, 'ZERO_OR_NULL', 'BAD_VALUE' ) p_mechanism
    from rdb$procedure_parameters pp
    where pp.rdb$procedure_name = upper('SP_TEST');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    P_NAME                          IN_ARG
    P_MECHANISM                     ZERO_OR_NULL

    P_NAME                          OUT_ARG
    P_MECHANISM                     ZERO_OR_NULL
"""

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

