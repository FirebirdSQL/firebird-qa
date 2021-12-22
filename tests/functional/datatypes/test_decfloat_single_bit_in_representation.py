#coding:utf-8
#
# id:           functional.datatypes.decfloat_single_bit_in_representation
# title:        DECFLOAT: check result of EXP() which can be represented only by one ("last") significant bit
# decription:   
#                   Get minimal distinguish from zero value for DEFCFLOAT datatype using EXP() function.
#                   Check some trivial arithmetic results for this value and pair of other values which are closest to it.
#                   See also: https://en.wikipedia.org/wiki/Decimal_floating_point
#                   Checked on 4.0.0.1714
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
         df0 as decfloat_near_zero
        ,df1 as min_decfloat_distinguish_from_zero
        ,df2 as max_decfloat_non_distinct_from_zero
        ,df0/df1 as division_result_1a
        ,df1/df0 as division_result_1b
        ,df0-df1 as subtract_result_1a
        ,df1-df0 as subtract_result_1b
        ,df0+df2 = df1 as sum_cmp_result_2
        ,df1 / df1 division_result_2
        ,df1+df2 = df1 sum_and_cmp_result_2
    from (
        select
            exp( cast( -14221.4586815117860898045324562520948 as decfloat) ) as df0
           ,exp( cast( -14221.4586815117860898045324562520949 as decfloat) ) as df1
           ,exp( cast( -14221.4586815117860898045324562520950 as decfloat) ) as df2
        from rdb$database 
    );
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DECFLOAT_NEAR_ZERO                                                 1E-6176
    MIN_DECFLOAT_DISTINGUISH_FROM_ZERO                                    1E-6176
    MAX_DECFLOAT_NON_DISTINCT_FROM_ZERO                                    0E-6176
    DIVISION_RESULT_1A                                                       1
    DIVISION_RESULT_1B                                                       1
    SUBTRACT_RESULT_1A                                                 0E-6176
    SUBTRACT_RESULT_1B                                                 0E-6176
    SUM_CMP_RESULT_2                  <true>
    DIVISION_RESULT_2                                                        1
    SUM_AND_CMP_RESULT_2            <true>
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

