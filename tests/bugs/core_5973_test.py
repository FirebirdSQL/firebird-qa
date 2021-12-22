#coding:utf-8
#
# id:           bugs.core_5973
# title:        Handling FP overflow in double precision value when converting from decfloat.
# decription:   
#                    Confirmed wrong result for numbers that have ABS greater than max double precision limit in: WI-T4.0.0.1340
#                    Works fine on: WI-T4.0.0.1457
#               
#                    09.12.2019.
#                    Updated syntax for SET BIND command because it was changed in 11-nov-2019. 
#                    Changed expected std_err: added text with "SQL error code = -303"
#               
#                    Checked on: WI-T4.0.0.1685, 1.38 s.
#                    05.03.2021: added subst.: max. floating point precision on Linux is 15 rather than on Windows (16 digits).
#                
# tracker_id:   CORE-5973
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('0.0000000000000000', '0.000000000000000')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    -- OLD SYNTAX: set decfloat bind double precision;
    -- Syntax after 11-nov-2019:
    -- https://github.com/FirebirdSQL/firebird/commit/a77295ba153e0c17061e2230d0ffdbaf08839114
    -- See also: doc/sql.extensions/README.set_bind.md:
    --     SET BIND OF type-from TO { type-to | LEGACY };
    --     SET BIND OF type NATIVE;

    set bind of decfloat to double precision;

    set decfloat traps to Overflow, Underflow;

    -- Following four statements should raise exception:
    -- #################################################


    -- Statement failed, SQLSTATE = 22003
    -- Decimal float overflow.  The exponent of a result is greater than the magnitude allowed.
    select cast( 9.999999999999999999999999999999999E6144 as decfloat(34)) as greatest_df34_for_pos_scope from rdb$database;
    select cast(-9.999999999999999999999999999999999E6144 as decfloat(34)) as freatest_df34_for_neg_scope from rdb$database;

    -- Statement failed, SQLSTATE = 22003
    -- Decimal float underflow.  The exponent of a result is less than the magnitude allowed.
    select cast(1.0E-6143 as decfloat(34)) as approx_zero_df34_for_pos_scope from rdb$database;
    select cast(-1.0E-6143 as decfloat(34)) as approx_zero__df34_for_neg_scope from rdb$database;


    set decfloat traps to Inexact;

    -- Following four statements should NOT raise exception and issue: Infinity, Infinity, 0.000..., 0.000...:
    -- ##############################################################

    --  This must issue Infinity instead of 0.000...:
    select cast( 9.999999999999999999999999999999999E6144 as decfloat(34)) as greatest_df34_for_pos_scope from rdb$database;

    --  This must issue -Infinity instead of 0.000...:
    select cast(-9.999999999999999999999999999999999E6144 as decfloat(34)) as greatest_df34_for_neg_scope from rdb$database;

    select cast(1.0E-6143 as decfloat(34)) as approx_zero_df34_for_pos_scope from rdb$database;
    
    select cast(-1.0E-6143 as decfloat(34)) as approx_zero_df34_for_neg_scope from rdb$database;

    quit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    GREATEST_DF34_FOR_POS_SCOPE     Infinity
    GREATEST_DF34_FOR_NEG_SCOPE     -Infinity
    APPROX_ZERO_DF34_FOR_POS_SCOPE  0.0000000000000000
    APPROX_ZERO_DF34_FOR_NEG_SCOPE  0.0000000000000000
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Dynamic SQL Error
    -SQL error code = -303
    -Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

    Statement failed, SQLSTATE = 22003
    Dynamic SQL Error
    -SQL error code = -303
    -Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.

    Statement failed, SQLSTATE = 22003
    Dynamic SQL Error
    -SQL error code = -303
    -Floating-point underflow.  The exponent of a floating-point operation is less than the magnitude allowed.

    Statement failed, SQLSTATE = 22003
    Dynamic SQL Error
    -SQL error code = -303
    -Floating-point underflow.  The exponent of a floating-point operation is less than the magnitude allowed.
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

