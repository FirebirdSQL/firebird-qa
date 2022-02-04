#coding:utf-8

"""
ID:          dp-single-bit-in-representation
TITLE:       Check result of EXP() which can be represented only by one ("last") significant bit
DESCRIPTION:
FBTEST:      functional.datatypes.dp_single_bit_in_representation
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    select iif(exp(-745.1332191)=0.0, 0, 1) as still_has_bits from rdb$database;
    select iif(exp(-745.1332192)=0.0, 0, 1) as still_has_bits from rdb$database;
    select e1,e2, iif(e1=e2, 'equals', 'differs') as e1_equ_e2,  e1/e2 as e1_div_e2, e2/e1 as e2_div_e2
    from (
        select exp(-744.0346068132731393) as e1, exp(-745.1332191019410399) as e2 from rdb$database
    );
"""

act = isql_act('db', test_script)

expected_stdout = """
    STILL_HAS_BITS                  1
    STILL_HAS_BITS                  0
    E1                              4.940656458412465e-324
    E2                              4.940656458412465e-324
    E1_EQU_E2                       equals
    E1_DIV_E2                       1.000000000000000
    E2_DIV_E2                       1.000000000000000
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
