#coding:utf-8
#
# id:           functional.datatypes.decfloat_boundary_values
# title:        Check BOUNDARY values that are defined for DECFLOAT datatype.
# decription:   
#                   See CORE-5535 and doc\\sql.extensions\\README.data_types
#                   FB40CS, build 4.0.0.651: OK, 1.906ss
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[\\s]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with 
    c as (
        select
             cast(-9.999999999999999E384 as decfloat(16)) as min_df16_for_neg_scope
            ,cast(-1.0E-383 as decfloat(16)) as max_df16_for_neg_scope
            ,cast(1.0E-383 as decfloat(16)) as min_df16_for_pos_scope
            ,cast( 9.999999999999999E384 as decfloat(16)) as max_df16_for_pos_scope
            ,cast(-9.999999999999999999999999999999999E6144 as decfloat(34)) as min_df34_for_neg_scope
            ,cast(-1.0E-6143 as decfloat(34)) as max_df34_for_neg_scope
            ,cast(1.0E-6143 as decfloat(34)) as min_df34_for_pos_scope
            ,cast( 9.999999999999999999999999999999999E6144 as decfloat(34)) as max_df34_for_pos_scope
        from rdb$database
    )
    select 
             c.min_df16_for_neg_scope
            ,c.max_df16_for_neg_scope
            ,c.min_df16_for_pos_scope
            ,c.max_df16_for_pos_scope
            ,c.min_df34_for_neg_scope
            ,c.max_df34_for_neg_scope
            ,c.min_df34_for_pos_scope
            ,c.max_df34_for_pos_scope
            ,c.min_df16_for_neg_scope - c.min_df16_for_neg_scope as zero_min_df16_for_neg
            ,c.max_df16_for_neg_scope - c.max_df16_for_neg_scope as zero_max_df16_for_neg
            ,c.min_df16_for_pos_scope - c.min_df16_for_pos_scope as zero_min_df16_for_pos
            ,c.max_df16_for_pos_scope - c.max_df16_for_pos_scope as zero_max_df16_for_pos
            ,c.min_df34_for_neg_scope - c.min_df34_for_neg_scope as zero_min_df34_for_neg
            ,c.max_df34_for_neg_scope - c.max_df34_for_neg_scope as zero_max_df34_for_neg
            ,c.min_df34_for_pos_scope - c.min_df34_for_pos_scope as zero_min_df34_for_pos
            ,c.max_df34_for_pos_scope - c.max_df34_for_pos_scope as zero_max_df34_for_pos
    from c
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MIN_DF16_FOR_NEG_SCOPE          -9.999999999999999E+384
    MAX_DF16_FOR_NEG_SCOPE                        -1.0E-383
    MIN_DF16_FOR_POS_SCOPE                         1.0E-383
    MAX_DF16_FOR_POS_SCOPE           9.999999999999999E+384
    MIN_DF34_FOR_NEG_SCOPE          -9.999999999999999999999999999999999E+6144
    MAX_DF34_FOR_NEG_SCOPE                                          -1.0E-6143
    MIN_DF34_FOR_POS_SCOPE                                           1.0E-6143
    MAX_DF34_FOR_POS_SCOPE           9.999999999999999999999999999999999E+6144
    ZERO_MIN_DF16_FOR_NEG                            0E+369
    ZERO_MAX_DF16_FOR_NEG                            0E-384
    ZERO_MIN_DF16_FOR_POS                            0E-384
    ZERO_MAX_DF16_FOR_POS                            0E+369
    ZERO_MIN_DF34_FOR_NEG                                              0E+6111
    ZERO_MAX_DF34_FOR_NEG                                              0E-6144
    ZERO_MIN_DF34_FOR_POS                                              0E-6144
    ZERO_MAX_DF34_FOR_POS                                              0E+6111
 """

@pytest.mark.version('>=4.0')
def test_decfloat_boundary_values_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

