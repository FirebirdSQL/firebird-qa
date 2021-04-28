#coding:utf-8
#
# id:           functional.datatypes.dp_single_bit_in_representation
# title:        Check result of EXP() which can be represented only by one ("last") significant bit
# decription:   
#                   build 2.5.8.27067: OK, 0.640s.
#                   build 3.0.3.32794: OK, 0.844s.
#                   build 4.0.0.700: OK, 0.922s.
#                   (2.5.8 was checked bot on Win32 and POSIX amd64; all others - only on Win32)
#                
# tracker_id:   
# min_versions: ['2.5.8']
# versions:     2.5.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select iif(exp(-745.1332191)=0.0, 0, 1) as still_has_bits from rdb$database;
    select iif(exp(-745.1332192)=0.0, 0, 1) as still_has_bits from rdb$database;
    select e1,e2, iif(e1=e2, 'equals', 'differs') as e1_equ_e2,  e1/e2 as e1_div_e2, e2/e1 as e2_div_e2
    from (
        select exp(-744.0346068132731393) as e1, exp(-745.1332191019410399) as e2 from rdb$database
    );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STILL_HAS_BITS                  1
    STILL_HAS_BITS                  0
    E1                              4.940656458412465e-324
    E2                              4.940656458412465e-324
    E1_EQU_E2                       equals
    E1_DIV_E2                       1.000000000000000
    E2_DIV_E2                       1.000000000000000
  """

@pytest.mark.version('>=2.5.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

