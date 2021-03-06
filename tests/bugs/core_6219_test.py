#coding:utf-8
#
# id:           bugs.core_6219
# title:        Add support for special (inf/nan) values when sorting DECFLOAT values
# decription:   
#                    Old descr: DECFLOAT values and queries with ORDER BY and/or windowed (analitical) functions.
#                    Confirmed wrong order of data in 4.0.0.1796.
#                    Checked on 4.0.0.1799 - all fine.
#                
# tracker_id:   CORE-6219
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set decfloat traps to;


    recreate table test0(n decfloat);
    commit;
     
    insert into test0 values( cast('-0' as decfloat ) );
    insert into test0 values( cast('NaN' as decfloat ) );
    insert into test0 values( cast('sNaN' as decfloat ) );
    insert into test0 values( cast('-NaN' as decfloat ) );
    insert into test0 values( cast('-SNaN' as decfloat ) );
    insert into test0 values( cast('0' as decfloat ) );
    insert into test0 values( cast('-inf' as decfloat ) );
    insert into test0 values( cast('-0.10' as decfloat ) );
    insert into test0 values( cast('0.10' as decfloat ) );
    insert into test0 values( cast('inf' as decfloat ) );
    insert into test0 values( cast('0.100' as decfloat ) );
    insert into test0 values( cast('-0.100' as decfloat ) );
    commit;

    -----------------------------------------------------------------------------

    select
         t.*
        ,iif( "-nan" < "-snan", '-nan LSS -snan', iif( "-nan" > "-snan", '-nan GTR -snan', iif("-nan" = "-snan", '-nan EQU -snan', 'UNKNOWN') ) ) as "Arithmetic: -nan vs to -snan:"
        ,iif( "-snan" < "-inf", '-snan LSS -inf', iif( "-snan" > "-inf", '-snan GTR -inf', iif("-snan" = "-inf", '-snan EQU -inf', 'UNKNOWN') ) ) as "Arithmetic: -snan vs to -inf:"
        ,iif( "-inf" < "-0.1", '-inf LSS -0.1', iif( "-inf" > "-0.1", '-inf GTR -0.1', iif("-inf" = "-0.1", '-inf EQU -0.1', 'UNKNOWN') ) ) as "Arithmetic: -inf vs to -0.1:"
        ,iif( "-0.1" < "-0.10", '-0.1 LSS -0.10', iif( "-0.1" > "-0.10", '-0.1 GTR -0.10', iif("-0.1" = "-0.10", '-0.1 EQU -0.10', 'UNKNOWN') ) ) as "Arithmetic: -0.1 vs to -0.10:"
        ,iif( "-0.10" < "-0", '-0.10 LSS -0', iif( "-0.10" > "-0", '-0.10 GTR -0', iif("-0.10" = "-0", '-0.10 EQU -0', 'UNKNOWN') ) ) as "Arithmetic: -0.10 vs to -0:"
        ,iif( "-0" < "0", '-0 LSS 0', iif( "-0" > "0", '-0 GTR 0', iif("-0" = "0", '-0 EQU 0', 'UNKNOWN') ) ) as "Arithmetic: -0 vs to 0:"
        ,iif( "0" < "0.10", '0 LSS 0.10', iif( "0" > "0.10", '0 GTR 0.10', iif("0" = "0.10", '0 EQU 0.10', 'UNKNOWN') ) ) as "Arithmetic: 0 vs to 0.10:"
        ,iif( "0.10" < "0.1", '0.10 LSS 0.1', iif( "0.10" > "0.1", '0.10 GTR 0.1', iif("0.10" = "0.1", '0.10 EQU 0.1', 'UNKNOWN') ) ) as "Arithmetic: 0.10 vs to 0.1:"
        ,iif( "0.1" < "inf", '0.1 LSS inf', iif( "0.1" > "inf", '0.1 GTR inf', iif("0.1" = "inf", '0.1 EQU inf', 'UNKNOWN') ) ) as "Arithmetic: 0.1 vs to inf:"
        ,iif( "inf" < "snan", 'inf LSS snan', iif( "inf" > "snan", 'inf GTR snan', iif("inf" = "snan", 'inf EQU snan', 'UNKNOWN') ) ) as "Arithmetic: inf vs to snan:"
        ,iif( "snan" < "nan", 'snan LSS nan', iif( "snan" > "nan", 'snan GTR nan', iif("snan" = "nan", 'snan EQU nan', 'UNKNOWN') ) ) as "Arithmetic: snan vs to nan:"
    from (
        select
            -cast('foo' as decfloat) as "-nan"
            ,-cast('snan' as decfloat) as "-snan"
            ,-cast(1/1e-9999 as decfloat) as "-inf"
            ,-cast(0.1 as decfloat) as "-0.1"
            ,-cast(0.10 as decfloat) as "-0.10"
            ,-cast(0 as decfloat) as "-0"
            ,cast(0 as decfloat) as "0"
            ,cast(0.10 as decfloat) as "0.10"
            ,cast(0.1 as decfloat) as "0.1"
            ,cast(1/1e-9999 as decfloat) as "inf"
            ,cast('snan' as decfloat) as "snan"
            ,cast('bar' as decfloat) as "nan"
        from rdb$database
    ) t; 

    -----------------------------------------------------------------------------
     
    select n as data_ordered_by_n from test0 order by n;

    select lead(n)over(order by n) as data_lead_n from test0;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    -nan                                                                  -NaN
    -snan                                                                -sNaN
    -inf                                                             -Infinity
    -0.1                                                                  -0.1
    -0.10                                                                -0.10
    -0                                                                      -0
    0                                                                        0
    0.10                                                                  0.10
    0.1                                                                    0.1
    inf                                                               Infinity
    snan                                                                  sNaN
    nan                                                                    NaN
    Arithmetic: -nan vs to -snan:   -nan EQU -snan
    Arithmetic: -snan vs to -inf:   -snan EQU -inf
    Arithmetic: -inf vs to -0.1:    -inf LSS -0.1
    Arithmetic: -0.1 vs to -0.10:   -0.1 EQU -0.10
    Arithmetic: -0.10 vs to -0:     -0.10 LSS -0
    Arithmetic: -0 vs to 0:         -0 EQU 0
    Arithmetic: 0 vs to 0.10:       0 LSS 0.10
    Arithmetic: 0.10 vs to 0.1:     0.10 EQU 0.1
    Arithmetic: 0.1 vs to inf:      0.1 LSS inf
    Arithmetic: inf vs to snan:     inf EQU snan
    Arithmetic: snan vs to nan:     snan EQU nan

    DATA_ORDERED_BY_N                                                     -NaN
    DATA_ORDERED_BY_N                                                    -sNaN
    DATA_ORDERED_BY_N                                                -Infinity
    DATA_ORDERED_BY_N                                                    -0.10
    DATA_ORDERED_BY_N                                                   -0.100
    DATA_ORDERED_BY_N                                                        0
    DATA_ORDERED_BY_N                                                       -0
    DATA_ORDERED_BY_N                                                     0.10
    DATA_ORDERED_BY_N                                                    0.100
    DATA_ORDERED_BY_N                                                 Infinity
    DATA_ORDERED_BY_N                                                     sNaN
    DATA_ORDERED_BY_N                                                      NaN

    DATA_LEAD_N                                                          -sNaN
    DATA_LEAD_N                                                      -Infinity
    DATA_LEAD_N                                                          -0.10
    DATA_LEAD_N                                                         -0.100
    DATA_LEAD_N                                                              0
    DATA_LEAD_N                                                             -0
    DATA_LEAD_N                                                           0.10
    DATA_LEAD_N                                                          0.100
    DATA_LEAD_N                                                       Infinity
    DATA_LEAD_N                                                           sNaN
    DATA_LEAD_N                                                            NaN
    DATA_LEAD_N                     <null>
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

