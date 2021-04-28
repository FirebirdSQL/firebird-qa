#coding:utf-8
#
# id:           bugs.core_4409
# title:        Enhancement in precision of calculations with NUMERIC/DECIMAL
# decription:   
#                  Checked on 4.0.0.767: OK, 0.828s.
#                  Reproduced wrong result on 4.0.0.748.
#                  See also letter to Alex, 12-jul-2017 09:49 (prototype for this test).
#                  --------------------
#                  ::: NB :::
#                  After fix CORE-5700 ("DECFLOAT underflow should yield zero instead of an error"), 02-feb-2018, expected result was 
#                  changed: all expressions with "almost zero" result should NOT raise any error.
#                  See also:
#                  https://github.com/FirebirdSQL/firebird/commit/a372f319f61d88151f5a34c4ee4ecdab6fe052f3
#                
# tracker_id:   CORE-4409
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
    recreate sequence g;
    commit;

    set list on;
    --set sqlda_display on;
    --set echo on;

    select gen_id(g,1) as "Test #", cast( 1e-308 as double precision ) positive_zero_e_308 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-309 as double precision ) positive_zero_e_309 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-310 as double precision ) positive_zero_e_310 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-320 as double precision ) positive_zero_e_320 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-321 as double precision ) positive_zero_e_321 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-322 as double precision ) positive_zero_e_322 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-323 as double precision ) positive_zero_e_323 from rdb$database;

    select gen_id(g,1) as "Test #", cast( 3.70550e-324 as double precision ) positive_zero_e324a from rdb$database;

    select gen_id(g,1) as "Test #", cast( 3.70549234380e-324 as double precision ) positive_zero_e324b from rdb$database;

    select gen_id(g,1) as "Test #", cast( 3.70549234381e-324 as double precision ) positive_zero_e324c from rdb$database;

    select gen_id(g,1) as "Test #", cast( 3.70548e-324 as double precision ) positive_zero_e324d from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-324 as double precision ) positive_zero_e324e from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-6176 as double precision ) positive_zero_e324f from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1e-6177 as double precision ) positive_zero_e324g from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1.79769313486231e+308 as double precision ) positive_inf_e308a from rdb$database;

    select gen_id(g,1) as "Test #", cast( 1.79769313486232e+308 as double precision ) positive_inf_e308b from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """

    Test #                          1
    POSITIVE_ZERO_E_308             9.999999999999999e-309



    Test #                          2
    POSITIVE_ZERO_E_309             0.0000000000000000



    Test #                          3
    POSITIVE_ZERO_E_310             0.0000000000000000



    Test #                          4
    POSITIVE_ZERO_E_320             0.0000000000000000



    Test #                          5
    POSITIVE_ZERO_E_321             0.0000000000000000



    Test #                          6
    POSITIVE_ZERO_E_322             0.0000000000000000



    Test #                          7
    POSITIVE_ZERO_E_323             0.0000000000000000



    Test #                          8
    POSITIVE_ZERO_E324A             0.0000000000000000



    Test #                          9
    POSITIVE_ZERO_E324B             0.0000000000000000



    Test #                          10
    POSITIVE_ZERO_E324C             0.0000000000000000



    Test #                          11
    POSITIVE_ZERO_E324D             0.0000000000000000



    Test #                          12
    POSITIVE_ZERO_E324E             0.0000000000000000



    Test #                          13
    POSITIVE_ZERO_E324F             0.0000000000000000



    Test #                          14
    POSITIVE_ZERO_E324G             0.0000000000000000



    Test #                          15
    POSITIVE_INF_E308A              1.797693134862310e+308
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Floating-point overflow.  The exponent of a floating-point operation is greater than the magnitude allowed.
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

