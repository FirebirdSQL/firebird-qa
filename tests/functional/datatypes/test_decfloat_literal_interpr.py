#coding:utf-8
#
# id:           functional.datatypes.decfloat_literal_interpr
# title:        Test interpretation of numeric literals.
# decription:   
#                   When literal can not be fit in any of "pre-4.0" then DECFLOAT should be considered as DECFLOAT(34).
#                   See CORE-5535 and doc\\sql.extensions\\README.data_types
#                   See also letter from Alex, 24.05.2017 19:28.
#               
#                   Checked on: FB40CS, build 4.0.0.651: OK, 1.375s
#                   ::: NB :::
#                   Currently only double precision form of literals is checked. 
#                   Literals with value out bigint scope are not checked - waiting for reply from Alex, letter 24.05.2017 21:16
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set sqlda_display on;

    select
        1e-308 as almost_zero_double_precision
    from rdb$database; -- ==> 9.999999999999999e-309 -- this is still DP

    select
        1e-309 as almost_zero_decfloat_34
    from rdb$database; -- ==> FAILS on 3.0; must be interpreted as DECFLOAT(34) on 4.0.0

    /*
    --- todo later! waiting for reply from Alex, letter 24.05.2017 21:16
    select 
        -9223372036854775809 as behind_bigint_max
        ,9223372036854775808 as behind_bigint_min
    from rdb$database; -- ==> FAILS on 3.0; must be interpreted as DECFLOAT(34) on 4.0.0
    */
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 0
    OUTPUT message field count: 1
    01: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
    :  name: CONSTANT  alias: ALMOST_ZERO_DOUBLE_PRECISION
    : table:   owner:
    ALMOST_ZERO_DOUBLE_PRECISION    9.999999999999999e-309
    INPUT message field count: 0
    OUTPUT message field count: 1
    01: sqltype: 32762 DECFLOAT(34) scale: 0 subtype: 0 len: 16
    :  name: CONSTANT  alias: ALMOST_ZERO_DECFLOAT_34
    : table:   owner:
    ALMOST_ZERO_DECFLOAT_34                                             1E-309
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

